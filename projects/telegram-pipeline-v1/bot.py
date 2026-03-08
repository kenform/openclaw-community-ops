#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import requests
import re
import tempfile
import subprocess
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.functions.channels import GetForumTopicsRequest
from telethon.errors.common import TypeNotFoundError
from telethon.utils import get_peer_id

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
MEMORY_PATH = BASE_DIR / "memory.json"
LOG_PATH = BASE_DIR / "userbot.log"


def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def setup_logger(debug: bool) -> logging.Logger:
    logger = logging.getLogger("tg_pipeline_v1")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG if debug else logging.INFO)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.DEBUG if debug else logging.INFO)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def extract_topic_id(message) -> Optional[int]:
    if not getattr(message, "reply_to", None):
        return None

    rt = message.reply_to
    # For forum topics in supergroups this is usually reply_to_top_id
    topic_id = getattr(rt, "reply_to_top_id", None)
    if topic_id:
        return topic_id

    # fallback for possible alternate shape
    return getattr(rt, "top_msg_id", None)


def format_payload(
    chat_title: str,
    chat_id: int,
    topic_id: Optional[int],
    text: str,
    media_only: bool,
    topic_title: Optional[str] = None,
) -> str:
    _ = (chat_title, chat_id, topic_id)
    title = topic_title.strip() if topic_title else "без названия"
    body = "[media message]" if media_only else (text.strip() if text else "[empty message]")
    return f"[TopicTitle: {title}]\n\n{body}"


EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U00002600-\U000026FF"
    "\U00002B00-\U00002BFF"
    "\U0001FA70-\U0001FAFF"
    "]+",
    flags=re.UNICODE,
)

DEFAULT_RULES = {
    "main_threshold": 3,
    "short_max_words": 6,
    "positive_3": ["лонг", "шорт", "беру", "взял", "заходим", "открываю", "открыл", "закрыл", "прикрыл", "фикс", "перезайду", "перезаходить"],
    "positive_2": ["позиция", "позиции", "позу", "поза", "тейк", "тейкнул", "стоп", "стопы", "держу", "жду тейк", "буду искать", "ищем позы", "дам позиции", "вход", "входы", "закреп"],
    "positive_1": ["btc", "биток", "eth", "эфир", "sol", "solana", "near", "ltc", "apt", "tia", "ordi", "link", "альта", "альты", "рынок", "монета", "фрс", "структура", "боковик", "откат", "коррекция", "разворот", "отскок", "цель"],
    "level_words": ["закреп под", "закреп над", "под красной зоной", "под зоной", "над зоной", "если пробьют", "если удержат", "если выкупят", "если не развернут", "будут давать вход", "цель", "локально", "выше идти", "к лоям", "в верх", "вверх", "вниз", "в разворот"],
    "negative_3": ["стрим", "эфир", "ютуб", "интра", "академия", "обучение", "набор", "бесплатно", "подписывайтесь", "инстаграм"],
    "negative_2": ["всем привет", "салам", "доброе утро", "вы там спите", "команда", "в офисе", "добавляйтесь", "пишите", "будкемп", "встреча", "билеты", "минск"],
    "short_pass_words": ["лонг", "шорт", "беру", "взял", "тейк", "фикс", "стоп", "цель", "вход", "закреп"],
    "asset_aliases": ["btc", "биток", "eth", "эфир", "sol", "solana", "near", "ltc", "apt", "tia", "ordi", "link", "zec", "alt", "альта"],
    "signal_threshold": 7,
}


def load_ilya_rules(cfg: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    rules = dict(DEFAULT_RULES)
    p = cfg.get("ILYA_RULES_PATH")
    if not p:
        return rules
    try:
        rp = Path(str(p))
        if not rp.is_absolute():
            rp = BASE_DIR / rp
        ext = json.loads(rp.read_text(encoding="utf-8"))
        if isinstance(ext, dict):
            rules.update(ext)
            logger.info("Loaded external Ilya rules: %s", rp)
    except Exception as e:
        logger.warning("Cannot load external Ilya rules (%s): %s", p, e)
    return rules


def _norm_text_for_filter(text: str) -> str:
    text = (text or "").lower()
    text = EMOJI_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_main_ilya_message(raw_text: str, has_media: bool, rules: Dict[str, Any]) -> Dict[str, Any]:
    text = _norm_text_for_filter(raw_text)
    if has_media and not text:
        return {"pass": False, "score": -999, "type": None, "reason": "DROP_NO_SIGNAL", "text": text}

    score = 0
    for w in rules.get("positive_3", []):
        if w in text: score += 3
    for w in rules.get("positive_2", []):
        if w in text: score += 2
    for w in rules.get("positive_1", []):
        if w in text: score += 1
    for w in rules.get("level_words", []):
        if w in text: score += 2

    neg3 = any(w in text for w in rules.get("negative_3", []))
    neg2 = any(w in text for w in rules.get("negative_2", []))
    if neg3: score -= 3
    if neg2: score -= 2

    words = [w for w in text.split(" ") if w]
    short_pass = len(words) <= int(rules.get("short_max_words", 6)) and any(w in text for w in rules.get("short_pass_words", []))

    msg_type = "VIEW"
    if any(w in text for w in ["закрыл", "прикрыл", "фикс", "тейк", "тейкнул"]): msg_type = "EXIT"
    elif any(w in text for w in ["лонг", "шорт", "беру", "взял", "заходим", "открываю", "открыл"]): msg_type = "ENTRY"
    elif any(w in text for w in rules.get("level_words", [])): msg_type = "LEVEL"
    elif any(w in text for w in ["держу", "позиция", "позиции", "поза", "позу"]): msg_type = "HOLD"
    elif any(w in text for w in ["перезайду", "перезаходить", "буду искать", "ищем позы", "вход", "входы"]): msg_type = "PLAN"

    is_pass = short_pass or score >= int(rules.get("main_threshold", 3))
    if is_pass:
        reason = {"ENTRY": "PASS_ENTRY", "HOLD": "PASS_HOLD", "EXIT": "PASS_EXIT", "PLAN": "PASS_PLAN", "LEVEL": "PASS_LEVEL", "VIEW": "PASS_VIEW"}.get(msg_type, "PASS_VIEW")
    else:
        if any(w in text for w in ["стрим", "ютуб", "эфир"]): reason = "DROP_STREAM"
        elif neg3: reason = "DROP_PROMO"
        elif neg2: reason = "DROP_SMALLTALK"
        else: reason = "DROP_NO_SIGNAL"

    return {"pass": is_pass, "score": score, "type": msg_type, "reason": reason, "text": text}


def parse_ilya_signal(raw_text: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    text = _norm_text_for_filter(raw_text)
    trash_patterns = ["заранее спасибо", "смотря на картину", "чисто", "а эту", "брали ?", "брали?"]
    if any(p in text for p in trash_patterns):
        return {
            "pass": False,
            "reason": "SIGNAL_NO_STRUCTURE",
            "confidence": 0,
            "asset": "UNKNOWN",
            "signal_type": "MARKET_VIEW",
            "bias": "—",
            "entry_condition": "—",
            "entry_zone": "—",
            "stop": "—",
            "target": "—",
            "timeframe": "—",
            "raw_text": text,
        }

    direction_words = ["лонг", "шорт", "лонгами", "шортить"]
    action_words = ["беру", "взял", "держу", "прикрыл", "закрыл", "перезайду", "открываю"]
    cond_words = ["закреп", "вход", "входы", "стоп", "цель", "если пробьют", "если удержат", "если выкупят", "будут давать вход"]
    bias_words = ["вверх", "вниз", "разворот", "отскок", "коррекция", "структура", "боковик", "к лоям", "выше идти"]

    has_dir = any(w in text for w in direction_words)
    has_action = any(w in text for w in action_words)
    has_cond = any(w in text for w in cond_words)
    has_bias = any(w in text for w in bias_words)
    is_question = ("?" in raw_text) or ("или" in text and ("лонг" in text or "шорт" in text))

    nums = re.findall(r"\b\d{2,6}(?:[\.,]\d+)?(?:\s*[kк])?(?:\s*[-–]\s*\d{2,6}(?:[\.,]\d+)?(?:\s*[kк])?)?\b", text)
    asset = "UNKNOWN"
    for a in rules.get("asset_aliases", []):
        if a in text:
            asset = a.upper()
            break

    signal_type = "MARKET_VIEW"
    if not is_question:
        if "лонг" in text and ("вход" in text or "беру" in text or "взял" in text): signal_type = "LONG_ENTRY"
        elif "шорт" in text and ("вход" in text or "беру" in text or "взял" in text): signal_type = "SHORT_ENTRY"
        elif "лонг" in text: signal_type = "LONG_SETUP"
        elif "шорт" in text: signal_type = "SHORT_SETUP"
    elif any(w in text for w in ["закрыл", "прикрыл", "фикс"]): signal_type = "EXIT"
    elif "держу" in text: signal_type = "HOLD"
    elif has_cond: signal_type = "CONDITIONAL_ENTRY"
    elif any(w in text for w in ["уровень", "закреп", "зона"]): signal_type = "LEVEL_UPDATE"

    confidence = 0
    confidence += 3 if has_dir else 0
    confidence += 3 if has_action else 0
    confidence += 3 if "цель" in text else 0
    confidence += 3 if len(nums) > 0 else 0
    confidence += 3 if asset != "UNKNOWN" else 0
    confidence += 2 if has_cond else 0
    confidence += 2 if has_bias else 0
    confidence += 2 if any(w in text for w in ["стоп", "закреп", "зона"]) else 0
    confidence -= 3 if is_question else 0
    if any(w in text for w in rules.get("negative_2", [])): confidence -= 2
    if any(w in text for w in ["стрим", "эфир", "в офисе", "интра"]): confidence -= 2

    zone_context = any(z in text for z in ["зона", "зону", "в зоне", "к зоне", "под зоной", "над зоной"])
    entry_zone = nums[0] if nums else "—"
    target = nums[1] if len(nums) > 1 else (nums[0] if ("цель" in text and nums and not zone_context) else "—")
    stop = "есть" if ("стоп" in text and not zone_context) else "—"
    timeframe = "—"
    tf = re.search(r"\b(\d+[mhd]|\d+\s*(мин|час|дн|дней))\b", text)
    if tf: timeframe = tf.group(1)

    threshold = int(rules.get("signal_threshold", 7))
    has_structure = bool(nums) or has_cond or (has_dir and has_action)
    weak_question = is_question and not has_structure
    signal_pass = confidence >= threshold and has_structure and not weak_question and not (asset == "UNKNOWN" and confidence <= threshold + 1)
    if signal_pass:
        reason = "SIGNAL_PASS"
    elif not has_structure or weak_question:
        reason = "SIGNAL_NO_STRUCTURE"
    elif confidence < threshold:
        reason = "SIGNAL_LOW_CONFIDENCE"
    elif asset == "UNKNOWN":
        reason = "SIGNAL_NO_ASSET"
    else:
        reason = "SIGNAL_DROP"

    return {
        "pass": signal_pass,
        "reason": reason,
        "confidence": confidence,
        "asset": asset,
        "signal_type": signal_type,
        "bias": "UP" if "вверх" in text else ("DOWN" if "вниз" in text else "—"),
        "entry_condition": "есть" if has_cond else "—",
        "entry_zone": entry_zone,
        "stop": stop,
        "target": target,
        "timeframe": timeframe,
        "raw_text": text,
    }


def format_signal_message(sig: Dict[str, Any]) -> str:
    return (
        "#IlyaSignal\n"
        f"Type: {sig.get('signal_type') or '—'}\n"
        f"Asset: {sig.get('asset') or '—'}\n"
        f"Bias: {sig.get('bias') or '—'}\n"
        f"Entry: {(sig.get('entry_condition') if sig.get('entry_condition') != '—' else sig.get('entry_zone')) or '—'}\n"
        f"Stop: {sig.get('stop') or '—'}\n"
        f"Target: {sig.get('target') or '—'}\n"
        f"Timeframe: {sig.get('timeframe') or '—'}\n"
        f"Confidence: {sig.get('confidence')}\n"
        f"Raw: {sig.get('raw_text') or '—'}"
    )


def transcribe_voice_with_whisper(media_bytes: Optional[bytes]) -> str:
    if not media_bytes:
        return ""
    try:
        with tempfile.TemporaryDirectory() as td:
            in_path = Path(td) / "voice.ogg"
            out_txt = Path(td) / "voice.txt"
            in_path.write_bytes(media_bytes)
            cmd = ["python3", "-m", "whisper", str(in_path), "--model", "tiny", "--language", "ru", "--output_format", "txt", "--output_dir", td]
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            if out_txt.exists():
                return out_txt.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return ""


async def transcribe_voice_preferred(client: TelegramClient, media_bytes: Optional[bytes], logger: logging.Logger) -> str:
    """MSK 07:00-19:00: try @voice_transcribot first, then Whisper fallback."""
    if not media_bytes:
        return ""

    # UTC+3 (MSK)
    msk_hour = (time.gmtime().tm_hour + 3) % 24
    use_voicebot_first = 7 <= msk_hour < 19

    if use_voicebot_first:
        try:
            with tempfile.TemporaryDirectory() as td:
                p = Path(td) / "voice.ogg"
                p.write_bytes(media_bytes)
                async with client.conversation("@voice_transcribot", timeout=90) as conv:
                    await conv.send_file(str(p), voice_note=True)
                    for _ in range(4):
                        resp = await conv.get_response(timeout=25)
                        txt = (getattr(resp, "raw_text", None) or getattr(resp, "message", "") or "").strip()
                        if txt and not txt.startswith("/"):
                            logger.info("Voice transcribed via @voice_transcribot")
                            return txt
        except Exception as e:
            logger.warning("@voice_transcribot failed, fallback whisper: %s", e)

    txt = transcribe_voice_with_whisper(media_bytes)
    if txt:
        logger.info("Voice transcribed via Whisper fallback")
    return txt


def classify_artur_main(text_raw: str) -> Dict[str, Any]:
    text = _norm_text_for_filter(text_raw)
    if not text:
        return {"pass": False, "reason": "DROP_NO_SIGNAL", "type": None}

    smalltalk = ["всем привет", "доброе утро", "красиво", "жесть", "работаем", "ну что", "как вам"]
    if any(w in text for w in smalltalk):
        return {"pass": False, "reason": "DROP_SMALLTALK", "type": None}

    hold_words = ["держу", "держим", "пока тяну позиции", "держу до стопа", "позицию держу", "не закрываю"]
    if any(w in text for w in hold_words):
        return {"pass": True, "reason": "PASS_HOLD", "type": "HOLD", "hold_only": True}

    return {"pass": True, "reason": "PASS_VIEW", "type": "VIEW", "hold_only": False}


def parse_artur_signal(text_raw: str) -> Dict[str, Any]:
    text = _norm_text_for_filter(text_raw)
    entry_words = ["лонг", "шорт", "шорчу", "взял", "беру", "открыл", "вход", "вход по рынку", "лимитка", "лимитный вход", "добавку лимиткой", "в сделку зашел"]
    stop_words = ["стоп", "stop", "стопы", "stop loss"]
    target_words = ["цель", "тейк", "тейки", "take"]

    has_entry = any(w in text for w in entry_words)
    has_stop = any(w in text for w in stop_words)
    has_target = any(w in text for w in target_words)

    # explicit levels
    entry_val = "—"
    stop_val = "—"
    target_val = "—"

    nums = re.findall(r"\b[A-Z]{2,8}/USDT\b|\b\d{1,6}(?:[\.,]\d+)?\b", text_raw.upper())
    levels = [n for n in nums if "/USDT" not in n]

    ms = re.search(r"(?:стоп|stop|stop loss)\s*[🛑:\-]?\s*(\d{1,6}(?:[\.,]\d+)?)", text, flags=re.IGNORECASE)
    mt = re.search(r"(?:цель|тейк|take)\s*[:\-]?\s*(\d{1,6}(?:[\.,]\d+)?)", text, flags=re.IGNORECASE)
    if ms:
        stop_val = ms.group(1)
    if mt:
        target_val = mt.group(1)
    if levels:
        entry_val = levels[0]

    asset = "UNKNOWN"
    asset_list = ["BTC", "ETH", "SOL", "APT", "LINK", "BCH", "MATIC", "ALT"]
    for a in asset_list:
        if a in text_raw.upper() or a.lower() in text:
            asset = a
            break
    m_pair = re.search(r"\b([A-Z]{2,8})/USDT\b", text_raw.upper())
    if m_pair:
        asset = m_pair.group(1)

    confidence = 0
    confidence += 3 if has_entry else 0
    confidence += 3 if has_stop else 0
    confidence += 3 if has_target else 0
    confidence += 2 if asset != "UNKNOWN" else 0
    confidence += 1 if bool(levels) else 0

    signal_pass = sum([has_entry, has_stop, has_target]) >= 2 and confidence >= 6
    if signal_pass:
        reason = "ARTUR_SIGNAL_PASS"
    elif confidence < 6:
        reason = "ARTUR_LOW_CONFIDENCE"
    else:
        reason = "ARTUR_SIGNAL_DROP"

    stype = "LONG_ENTRY" if "лонг" in text else ("SHORT_ENTRY" if "шорт" in text or "шорчу" in text else "LONG_ENTRY")

    return {
        "pass": signal_pass,
        "reason": reason,
        "confidence": confidence,
        "asset": asset,
        "signal_type": stype,
        "entry": entry_val,
        "stop": stop_val,
        "target": target_val,
        "raw": text_raw.strip() or "—",
    }


def format_artur_signal(sig: Dict[str, Any]) -> str:
    return (
        "#ArturSignal\n\n"
        f"Asset: {sig.get('asset','UNKNOWN')}\n"
        f"Type: {sig.get('signal_type','—')}\n"
        f"Entry: {sig.get('entry','—')}\n"
        f"Stop: {sig.get('stop','—')}\n"
        f"Target: {sig.get('target','—')}\n"
        f"Confidence: {sig.get('confidence',0)}\n\n"
        "Raw:\n"
        f"{sig.get('raw','—')}"
    )


def _chunk_text(text: str, limit: int = 3500):
    text = text or ""
    if len(text) <= limit:
        return [text]
    parts = []
    rest = text
    while rest:
        if len(rest) <= limit:
            parts.append(rest)
            break
        cut = rest.rfind("\n", 0, limit)
        if cut < 200:
            cut = limit
        parts.append(rest[:cut])
        rest = rest[cut:].lstrip("\n")
    return parts


def _post_bot_api(bot_token: str, method: str, logger: logging.Logger, *, json_payload=None, data_payload=None, files=None) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    for attempt in range(1, 4):
        try:
            if json_payload is not None:
                r = requests.post(url, json=json_payload, timeout=40)
            else:
                r = requests.post(url, data=data_payload, files=files, timeout=60)
            if r.status_code == 429:
                retry_after = r.json().get("parameters", {}).get("retry_after", 2)
                logger.warning("Bot API rate limit. retry_after=%s", retry_after)
                time.sleep(retry_after)
                continue
            if r.status_code >= 400:
                logger.error("Bot API %s: %s", r.status_code, r.text[:300])
            r.raise_for_status()
            data = r.json()
            if not data.get("ok"):
                logger.error("Bot API responded ok=false: %s", data)
                return False
            return True
        except requests.RequestException as e:
            logger.error("Bot API %s attempt %s/3 failed: %s", method, attempt, e)
            time.sleep(1.5 * attempt)
    return False


def send_via_bot_api(
    bot_token: str,
    target_channel_id: str,
    text: str,
    logger: logging.Logger,
    dry_run: bool = False,
    media_kind: Optional[str] = None,
    media_bytes: Optional[bytes] = None,
    media_name: str = "media.bin",
) -> bool:
    chunks = _chunk_text(text)
    first_chunk = chunks[0] if chunks else ""

    if dry_run:
        logger.info("[DRY_RUN] Skip send. media=%s chunks=%s first_payload:\n%s", media_kind, len(chunks), first_chunk)
        return True

    if media_kind and media_bytes is not None:
        method_map = {
            "photo": ("sendPhoto", "photo"),
            "video": ("sendVideo", "video"),
            "voice": ("sendVoice", "voice"),
            "document": ("sendDocument", "document"),
        }
        if media_kind in method_map:
            method, field = method_map[media_kind]
            ok = _post_bot_api(
                bot_token,
                method,
                logger,
                data_payload={"chat_id": target_channel_id, "caption": first_chunk or "[media message]"},
                files={field: (media_name, media_bytes)},
            )
            if not ok:
                return False
            if len(chunks) > 1:
                for extra in chunks[1:]:
                    if not _post_bot_api(
                        bot_token,
                        "sendMessage",
                        logger,
                        json_payload={"chat_id": target_channel_id, "text": extra, "disable_web_page_preview": True},
                    ):
                        return False
            return True

    for chunk in chunks:
        if not _post_bot_api(
            bot_token,
            "sendMessage",
            logger,
            json_payload={"chat_id": target_channel_id, "text": chunk, "disable_web_page_preview": True},
        ):
            return False
    return True


def parse_ref(value: Union[int, str]) -> Union[int, str]:
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if s.startswith("-100") or (s.startswith("-") and s[1:].isdigit()) or s.isdigit():
        try:
            return int(s)
        except Exception:
            return s
    if s.startswith("https://t.me/"):
        return s.rsplit("/", 1)[-1].lstrip("@")
    return s.lstrip("@")


async def resolve_chat_ref(client: TelegramClient, ref: Union[int, str]) -> Optional[int]:
    if isinstance(ref, int):
        return ref
    try:
        entity = await client.get_entity(ref)
        return int(getattr(entity, "id")) if getattr(entity, "id", None) is not None else None
    except Exception:
        return None


async def resolve_from_folder(client: TelegramClient, folder_name: str, logger: logging.Logger):
    channel_ids: Set[int] = set()
    group_ids: Set[int] = set()

    try:
        filters_resp = await client(GetDialogFiltersRequest())
        filters = getattr(filters_resp, "filters", filters_resp)
    except Exception as e:
        logger.error("Cannot load Telegram folders: %s", e)
        return channel_ids, group_ids

    target = None
    normalized = folder_name.strip().lower()

    for f in filters:
        title = getattr(f, "title", None)
        title_str = str(title) if title is not None else ""
        if title_str.strip().lower() == normalized:
            target = f
            break

    if not target:
        # fuzzy fallback: contains
        for f in filters:
            title = getattr(f, "title", None)
            title_str = str(title) if title is not None else ""
            if normalized and normalized in title_str.strip().lower():
                target = f
                logger.info("Folder fuzzy-matched: requested='%s' matched='%s'", folder_name, title_str)
                break

    if not target:
        logger.warning("Folder '%s' not found", folder_name)
        return channel_ids, group_ids

    peers = getattr(target, "include_peers", []) or []
    for p in peers:
        try:
            entity = await client.get_entity(p)
            chat_id = int(get_peer_id(entity))
            if not chat_id:
                continue

            # broadcast=True => channel, megagroup=True => group
            if getattr(entity, "broadcast", False):
                channel_ids.add(chat_id)
            elif getattr(entity, "megagroup", False):
                group_ids.add(chat_id)
            else:
                # fallback to channel bucket
                channel_ids.add(chat_id)
        except Exception:
            continue

    return channel_ids, group_ids


def main() -> None:
    cfg = load_json(CONFIG_PATH, default={})

    required = [
        "TELEGRAM_API_ID",
        "TELEGRAM_API_HASH",
        "SESSION_NAME",
        "BOT_TOKEN",
        "TARGET_CHANNEL_ID",
        "DRY_RUN",
    ]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise SystemExit(f"Missing config keys: {', '.join(missing)}")

    folder_mode = bool(cfg.get("ALLOWED_FOLDER_NAME"))

    if not folder_mode and "ALLOWED_CHANNEL_IDS" not in cfg and "ALLOWED_CHANNELS" not in cfg:
        raise SystemExit("Missing config key: ALLOWED_CHANNELS (or ALLOWED_CHANNEL_IDS), or set ALLOWED_FOLDER_NAME")

    if not folder_mode and "ALLOWED_GROUP_ID" not in cfg and "ALLOWED_GROUP" not in cfg:
        raise SystemExit("Missing config key: ALLOWED_GROUP (or ALLOWED_GROUP_ID), or set ALLOWED_FOLDER_NAME")

    debug = bool(cfg.get("DEBUG", False))
    logger = setup_logger(debug=debug)

    state = load_json(
        MEMORY_PATH,
        default={
            "processed_total": 0,
            "last_event": None,
        },
    )

    api_id = int(cfg["TELEGRAM_API_ID"])
    api_hash = str(cfg["TELEGRAM_API_HASH"])
    session_name = str(cfg["SESSION_NAME"])
    bot_token = str(cfg["BOT_TOKEN"])
    main_target_ref = parse_ref(cfg.get("MAIN_TARGET_CHANNEL_ID", cfg["TARGET_CHANNEL_ID"]))
    signal_target_ref = parse_ref(cfg.get("SIGNAL_TARGET_CHANNEL_ID", cfg.get("TARGET_CHANNEL_ID")))

    raw_channels = cfg.get("ALLOWED_CHANNELS", cfg.get("ALLOWED_CHANNEL_IDS", []))
    raw_group = cfg.get("ALLOWED_GROUP", cfg.get("ALLOWED_GROUP_ID"))

    allowed_channel_refs = [parse_ref(x) for x in raw_channels]
    allowed_group_ref = parse_ref(raw_group) if raw_group is not None else None
    allowed_folder_name = str(cfg.get("ALLOWED_FOLDER_NAME", "")).strip()
    include_manual_when_folder = bool(cfg.get("INCLUDE_ALLOWED_CHANNELS_WHEN_FOLDER", False))

    dry_run = bool(cfg["DRY_RUN"])

    topic_filter_enabled = bool(cfg.get("TOPIC_FILTER_ENABLED", False))
    ilya_main_filter_enabled = bool(cfg.get("ILYA_MAIN_FILTER_ENABLED", True))
    signal_parser_enabled = bool(cfg.get("SIGNAL_PARSER_ENABLED", True))
    ilya_topic_id = int(cfg.get("ILYA_TOPIC_ID", 58866))
    artur_enabled = bool(cfg.get("ARTUR_ENABLED", True))
    artur_channel_ref = parse_ref(cfg.get("ARTUR_CHANNEL_ID", -1001699376756))
    artur_topic_id = int(cfg.get("ARTUR_TOPIC_ID", 57974))
    allowed_topic_ids = {int(x) for x in cfg.get("ALLOWED_TOPIC_IDS", []) if str(x).strip().isdigit()}
    if ilya_topic_id not in allowed_topic_ids:
        allowed_topic_ids.add(ilya_topic_id)
    blocked_channel_ids = {int(x) for x in cfg.get("BLOCKED_CHANNEL_IDS", []) if str(x).strip().lstrip('-').isdigit()}
    track_group_only = bool(cfg.get("TRACK_GROUP_ONLY", False))
    backfill_enabled = bool(cfg.get("BACKFILL_ENABLED", False))
    rules = load_ilya_rules(cfg, logger)
    rules["signal_threshold"] = int(cfg.get("SIGNAL_CONFIDENCE_THRESHOLD", rules.get("signal_threshold", 7)))

    logger.info("Starting pipeline. dry_run=%s, debug=%s", dry_run, debug)
    logger.info("Allowed channel refs=%s, allowed_group_ref=%s", allowed_channel_refs, allowed_group_ref)
    logger.info("Topic filter: enabled=%s allowed_topic_ids=%s", topic_filter_enabled, sorted(list(allowed_topic_ids)))
    logger.info("Blocked channel ids=%s", sorted(list(blocked_channel_ids)))
    logger.info("Folder mode: name=%s include_manual_when_folder=%s", allowed_folder_name or None, include_manual_when_folder)
    logger.info("Track group only=%s", track_group_only)
    logger.info("Backfill enabled=%s (pipeline handles new incoming only)", backfill_enabled)
    logger.info("Ilya filter enabled=%s signal_parser_enabled=%s ilya_topic_id=%s", ilya_main_filter_enabled, signal_parser_enabled, ilya_topic_id)
    logger.info("Artur enabled=%s artur_channel_ref=%s artur_topic_id=%s", artur_enabled, artur_channel_ref, artur_topic_id)

    client = TelegramClient(session_name, api_id, api_hash, auto_reconnect=True, sequential_updates=True)

    allowed_channel_ids: Set[int] = set()
    allowed_group_id: Optional[int] = None
    main_target_channel_id: Optional[Union[int, str]] = None
    signal_target_channel_id: Optional[Union[int, str]] = None
    topic_title_map: Dict[int, str] = {}
    allowed_topic_runtime_ids: Set[int] = set(allowed_topic_ids)
    artur_topic_runtime_ids: Set[int] = {artur_topic_id}
    artur_channel_id: Optional[int] = None

    should_stop = {"value": False}

    def _shutdown(*_args):
        should_stop["value"] = True
        logger.info("Shutdown signal received")
        try:
            if client.is_connected():
                client.loop.create_task(client.disconnect())
        except Exception:
            pass

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    async def refresh_topic_title_map(group_id: Optional[int]):
        nonlocal topic_title_map, allowed_topic_runtime_ids, artur_topic_runtime_ids
        if not group_id:
            topic_title_map = {}
            allowed_topic_runtime_ids = set(allowed_topic_ids)
            return
        try:
            entity = await client.get_entity(group_id)
            resp = await client(GetForumTopicsRequest(channel=entity, offset_date=None, offset_id=0, offset_topic=0, limit=200, q=""))
            topics = getattr(resp, "topics", []) or []
            topic_title_map = {}
            resolved_runtime = set()
            for t in topics:
                t_title = str(getattr(t, "title", "")).strip()
                t_top = int(getattr(t, "top_message", 0) or 0)
                t_id = int(getattr(t, "id", 0) or 0)
                if t_top:
                    topic_title_map[t_top] = t_title
                if t_id:
                    topic_title_map[t_id] = t_title

                if t_top in allowed_topic_ids or t_id in allowed_topic_ids:
                    if t_top:
                        resolved_runtime.add(t_top)
                    if t_id:
                        resolved_runtime.add(t_id)
            allowed_topic_runtime_ids = resolved_runtime or set(allowed_topic_ids)

            artur_resolved = set()
            for t in topics:
                t_top = int(getattr(t, "top_message", 0) or 0)
                t_id = int(getattr(t, "id", 0) or 0)
                if t_top == artur_topic_id or t_id == artur_topic_id:
                    if t_top:
                        artur_resolved.add(t_top)
                    if t_id:
                        artur_resolved.add(t_id)
            artur_topic_runtime_ids = artur_resolved or {artur_topic_id}

            logger.info("Loaded topic titles: %s", {k: topic_title_map[k] for k in sorted(topic_title_map)[:20]})
            logger.info("Resolved runtime topic ids=%s", sorted(list(allowed_topic_runtime_ids)))
            logger.info("Resolved artur topic runtime ids=%s", sorted(list(artur_topic_runtime_ids)))
        except Exception as e:
            logger.warning("Cannot load forum topic titles: %s", e)
            topic_title_map = {}
            allowed_topic_runtime_ids = set(allowed_topic_ids)

    @client.on(events.NewMessage(incoming=True))
    async def on_new_message(event):
        chat_id = int(event.chat_id)

        if chat_id in blocked_channel_ids:
            logger.warning("Blocked channel skipped: chat_id=%s message_id=%s", chat_id, getattr(event.message, 'id', None))
            return

        if track_group_only and chat_id != allowed_group_id and chat_id != artur_channel_id:
            return

        if chat_id not in allowed_channel_ids and chat_id != allowed_group_id:
            return

        try:
            msg = event.message
            chat = await event.get_chat()
            chat_title = getattr(chat, "title", None) or getattr(chat, "username", None) or str(chat_id)
            topic_id = extract_topic_id(msg)

            topic_title = topic_title_map.get(topic_id) if topic_id else None
            text = msg.message or ""
            media_only = bool(msg.media) and not text.strip()

            is_ilya = chat_id == allowed_group_id and topic_id in allowed_topic_runtime_ids
            is_artur_topic = artur_enabled and chat_id == allowed_group_id and topic_id in artur_topic_runtime_ids
            is_artur_channel = artur_enabled and artur_channel_id is not None and chat_id == artur_channel_id
            if not (is_ilya or is_artur_topic or is_artur_channel):
                logger.info("Dropped (source not configured): chat_id=%s topic_id=%s msg_id=%s", chat_id, topic_id, msg.id)
                return

            media_kind = None
            media_bytes = None
            media_name = "media.bin"
            if msg.media:
                try:
                    if getattr(msg, "photo", None):
                        media_kind = "photo"; media_name = f"photo_{msg.id}.jpg"
                    elif getattr(msg, "video", None):
                        media_kind = "video"; media_name = f"video_{msg.id}.mp4"
                    elif getattr(msg, "voice", None):
                        media_kind = "voice"; media_name = f"voice_{msg.id}.ogg"
                    elif getattr(msg, "document", None):
                        media_kind = "document"; media_name = f"document_{msg.id}.bin"
                    if media_kind:
                        media_bytes = await client.download_media(msg, file=bytes)
                except Exception as e:
                    logger.warning("Media download failed, fallback to text only: msg_id=%s err=%s", msg.id, e)
                    media_kind = None; media_bytes = None

            if is_artur_topic or is_artur_channel:
                if media_kind == "voice" and not text.strip():
                    text = await transcribe_voice_preferred(client, media_bytes, logger)
                    media_only = bool(msg.media) and not text.strip()
                main_result = classify_artur_main(text)
            else:
                main_result = classify_main_ilya_message(text, has_media=bool(msg.media), rules=rules) if ilya_main_filter_enabled else {"pass": True, "score": 0, "type": "VIEW", "reason": "PASS_VIEW"}

            if not main_result["pass"]:
                logger.info("%s score=%s msg_id=%s topic_id=%s", main_result.get("reason"), main_result.get("score", 0), msg.id, topic_id)

            sent_main = False
            if main_result["pass"] and main_target_channel_id is not None:
                payload = f"[Type: {main_result.get('type') or 'VIEW'}]\n" + format_payload(chat_title, chat_id, topic_id, text, media_only, topic_title=topic_title)
                sent_main = send_via_bot_api(
                    bot_token,
                    str(main_target_channel_id),
                    payload,
                    logger,
                    dry_run=dry_run,
                    media_kind=media_kind,
                    media_bytes=media_bytes,
                    media_name=media_name,
                )

            if signal_parser_enabled and signal_target_channel_id is not None and not main_result.get("hold_only", False):
                if is_artur_topic or is_artur_channel:
                    if not text.strip():
                        sig = {"pass": False, "reason": "ARTUR_SIGNAL_DROP", "confidence": 0}
                    else:
                        sig = parse_artur_signal(text)
                    if sig.get("pass"):
                        sig_msg = format_artur_signal(sig)
                        sig_ok = send_via_bot_api(bot_token, str(signal_target_channel_id), sig_msg, logger, dry_run=dry_run)
                        logger.info("%s confidence=%s msg_id=%s", "ARTUR_SIGNAL_PASS" if sig_ok else "ARTUR_SIGNAL_DROP", sig.get("confidence"), msg.id)
                    else:
                        logger.info("%s confidence=%s msg_id=%s", sig.get("reason"), sig.get("confidence"), msg.id)
                else:
                    sig = parse_ilya_signal(text, rules)
                    if sig["pass"]:
                        sig_msg = format_signal_message(sig)
                        sig_ok = send_via_bot_api(bot_token, str(signal_target_channel_id), sig_msg, logger, dry_run=dry_run)
                        logger.info("%s confidence=%s msg_id=%s topic_id=%s", "SIGNAL_PASS" if sig_ok else "SIGNAL_DROP", sig["confidence"], msg.id, topic_id)
                    else:
                        logger.info("%s confidence=%s msg_id=%s topic_id=%s", sig["reason"], sig["confidence"], msg.id, topic_id)

            if sent_main:
                state["processed_total"] = int(state.get("processed_total", 0)) + 1
                state["last_event"] = {
                    "chat_id": chat_id,
                    "chat_title": chat_title,
                    "message_id": msg.id,
                    "topic_id": topic_id,
                    "timestamp": int(time.time()),
                }
                save_json(MEMORY_PATH, state)
                logger.info("Forwarded message %s from %s", msg.id, chat_title)
        except FloodWaitError as e:
            logger.warning("FloodWaitError: sleep %ss", e.seconds)
            time.sleep(e.seconds)
        except RPCError as e:
            logger.error("Telethon RPC error: %s", e)
        except Exception as e:
            logger.exception("Unhandled pipeline error: %s", e)

    async def runner():
        nonlocal allowed_channel_ids, allowed_group_id, main_target_channel_id, signal_target_channel_id, artur_channel_id

        await client.start()
        me = await client.get_me()
        logger.info("Reader authorized as %s", getattr(me, "username", me.id))

        # Resolve refs -> numeric ids where possible
        resolved_channels: Set[int] = set()
        resolved_group_ids: Set[int] = set()

        if allowed_folder_name:
            folder_channels, folder_groups = await resolve_from_folder(client, allowed_folder_name, logger)
            resolved_channels.update(folder_channels)
            resolved_group_ids.update(folder_groups)
            logger.info(
                "Folder '%s' resolved: channels=%s groups=%s",
                allowed_folder_name,
                sorted(list(folder_channels)),
                sorted(list(folder_groups)),
            )

        if (not allowed_folder_name) or include_manual_when_folder:
            for ref in allowed_channel_refs:
                rid = await resolve_chat_ref(client, ref)
                if rid is None:
                    logger.warning("Cannot resolve channel ref: %s", ref)
                    continue
                if isinstance(ref, int):
                    resolved_channels.add(ref)
                else:
                    try:
                        ent_full = await client.get_entity(ref)
                        resolved_channels.add(int(get_peer_id(ent_full)))
                    except Exception:
                        resolved_channels.add(rid)

        grp = None
        if allowed_group_ref is not None:
            grp = await resolve_chat_ref(client, allowed_group_ref)
            if grp is None:
                logger.warning("Cannot resolve allowed group ref: %s", allowed_group_ref)

        if artur_enabled:
            ac = await resolve_chat_ref(client, artur_channel_ref)
            if ac is not None:
                artur_channel_id = int(ac)
                allowed_channel_ids.add(int(ac))
            else:
                logger.warning("Cannot resolve ARTUR channel ref: %s", artur_channel_ref)

        main_tgt = await resolve_chat_ref(client, main_target_ref)
        if main_tgt is None:
            logger.warning("Cannot resolve MAIN target channel ref: %s", main_target_ref)
            main_target_channel_id = str(main_target_ref)
        else:
            if isinstance(main_target_ref, int):
                main_target_channel_id = main_target_ref
            else:
                try:
                    ent_full = await client.get_entity(main_target_ref)
                    main_target_channel_id = int(get_peer_id(ent_full))
                except Exception:
                    main_target_channel_id = main_tgt

        signal_tgt = await resolve_chat_ref(client, signal_target_ref)
        if signal_tgt is None:
            logger.warning("Cannot resolve SIGNAL target channel ref: %s", signal_target_ref)
            signal_target_channel_id = str(signal_target_ref)
        else:
            if isinstance(signal_target_ref, int):
                signal_target_channel_id = signal_target_ref
            else:
                try:
                    ent_full = await client.get_entity(signal_target_ref)
                    signal_target_channel_id = int(get_peer_id(ent_full))
                except Exception:
                    signal_target_channel_id = signal_tgt

        allowed_channel_ids = resolved_channels
        if artur_channel_id is not None:
            allowed_channel_ids.add(int(artur_channel_id))

        if grp is not None:
            allowed_group_id = int(grp)
        elif allowed_group_ref is not None:
            allowed_group_id = int(allowed_group_ref) if isinstance(allowed_group_ref, int) else None
        elif resolved_group_ids:
            allowed_group_id = sorted(list(resolved_group_ids))[0]
            if len(resolved_group_ids) > 1:
                logger.warning(
                    "Folder contains multiple groups. Using first=%s. Set ALLOWED_GROUP to pin specific one.",
                    allowed_group_id,
                )
        else:
            allowed_group_id = None

        await refresh_topic_title_map(allowed_group_id)

        logger.info("Resolved allowed_channel_ids=%s", sorted(list(allowed_channel_ids)))
        logger.info("Resolved allowed_group_id=%s", allowed_group_id)
        logger.info("Resolved main_target_channel_id=%s", main_target_channel_id)
        logger.info("Resolved signal_target_channel_id=%s", signal_target_channel_id)

        # HARD SAFETY GUARD: never send to source channels/group
        source_ids = set(allowed_channel_ids)
        if allowed_group_id is not None:
            source_ids.add(int(allowed_group_id))

        for target_label, target_value in [("MAIN", main_target_channel_id), ("SIGNAL", signal_target_channel_id)]:
            try:
                tgt_int = int(target_value) if target_value is not None else None
            except Exception:
                tgt_int = None
            if tgt_int is not None and tgt_int in source_ids:
                raise RuntimeError(
                    f"Safety guard triggered: {target_label}_TARGET points to a source chat. "
                    "Refusing to start to prevent any write into source group/topics."
                )

        while not should_stop["value"]:
            if not client.is_connected():
                logger.warning("Client disconnected. Attempting reconnect...")
                try:
                    await client.connect()
                except Exception as e:
                    logger.error("Reconnect failed: %s", e)
                    await asyncio.sleep(3)
                    continue

            try:
                await client.run_until_disconnected()
            except TypeNotFoundError as e:
                logger.warning("Telethon update decode glitch (TypeNotFoundError). Reconnecting: %s", e)
                try:
                    await client.disconnect()
                except Exception:
                    pass
                await asyncio.sleep(2)
                continue
            except Exception as e:
                logger.error("run_until_disconnected error: %s", e)
                try:
                    await client.disconnect()
                except Exception:
                    pass
                await asyncio.sleep(3)
                continue

    try:
        with client:
            client.loop.run_until_complete(runner())
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        raise


if __name__ == "__main__":
    main()

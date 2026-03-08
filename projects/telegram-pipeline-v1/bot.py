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

POSITIVE_3 = ["лонг", "шорт", "беру", "взял", "заходим", "открываю", "закрыл", "прикрыл", "фикс"]
POSITIVE_2 = ["позиция", "поза", "тейк", "тейкнул", "стоп", "стопы", "держу", "перезайду"]
POSITIVE_1 = ["btc", "биток", "eth", "эфир", "sol", "solana", "альта", "альты", "рынок", "монета"]
LEVEL_WORDS = ["закреп", "уровень", "под зоной", "над зоной", "под красной зоной"]
NEGATIVE_3 = ["стрим", "эфир", "ютуб", "интра", "академия", "обучение", "набор"]
NEGATIVE_2 = ["всем привет", "салам", "доброе утро", "вы там спите", "команда", "в офисе"]
SHORT_PASS_WORDS = ["лонг", "шорт", "беру", "взял", "тейк", "фикс"]


def _norm_text_for_filter(text: str) -> str:
    text = (text or "").lower()
    text = EMOJI_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_ilya_message(raw_text: str, has_media: bool = False) -> Dict[str, Any]:
    text = _norm_text_for_filter(raw_text)

    if has_media and not text:
        return {"pass": False, "score": -999, "type": None, "reason": "DROP_NO_SIGNAL"}

    score = 0

    for w in POSITIVE_3:
        if w in text:
            score += 3
    for w in POSITIVE_2:
        if w in text:
            score += 2
    for w in POSITIVE_1:
        if w in text:
            score += 1
    for w in LEVEL_WORDS:
        if w in text:
            score += 2

    negative3_hit = any(w in text for w in NEGATIVE_3)
    negative2_hit = any(w in text for w in NEGATIVE_2)
    if negative3_hit:
        score -= 3
    if negative2_hit:
        score -= 2

    words = [w for w in text.split(" ") if w]
    short_pass = len(words) <= 6 and any(w in text for w in SHORT_PASS_WORDS)

    msg_type = None
    if any(w in text for w in ["закрыл", "прикрыл", "фикс", "тейк", "тейкнул"]):
        msg_type = "EXIT"
    elif any(w in text for w in ["лонг", "шорт", "беру", "взял", "заходим", "открываю"]):
        msg_type = "ENTRY"
    elif any(w in text for w in LEVEL_WORDS):
        msg_type = "LEVEL"
    elif any(w in text for w in ["держу", "позиция", "поза"]):
        msg_type = "HOLD"
    elif any(w in text for w in ["перезайду", "план", "подготов"]):
        msg_type = "PLAN"

    is_pass = short_pass or score >= 3

    if is_pass:
        if msg_type == "ENTRY":
            reason = "PASS_ENTRY"
        elif msg_type == "HOLD":
            reason = "PASS_HOLD"
        elif msg_type == "EXIT":
            reason = "PASS_EXIT"
        elif msg_type == "PLAN":
            reason = "PASS_PLAN"
        elif msg_type == "LEVEL":
            reason = "PASS_LEVEL"
        else:
            reason = "PASS_PLAN"
    else:
        if negative3_hit:
            reason = "DROP_PROMO"
        elif negative2_hit:
            reason = "DROP_SMALLTALK"
        else:
            reason = "DROP_NO_SIGNAL"

    return {"pass": is_pass, "score": score, "type": msg_type, "reason": reason, "text": text}


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
    target_channel_ref = parse_ref(cfg["TARGET_CHANNEL_ID"])

    raw_channels = cfg.get("ALLOWED_CHANNELS", cfg.get("ALLOWED_CHANNEL_IDS", []))
    raw_group = cfg.get("ALLOWED_GROUP", cfg.get("ALLOWED_GROUP_ID"))

    allowed_channel_refs = [parse_ref(x) for x in raw_channels]
    allowed_group_ref = parse_ref(raw_group) if raw_group is not None else None
    allowed_folder_name = str(cfg.get("ALLOWED_FOLDER_NAME", "")).strip()
    include_manual_when_folder = bool(cfg.get("INCLUDE_ALLOWED_CHANNELS_WHEN_FOLDER", False))

    dry_run = bool(cfg["DRY_RUN"])

    topic_filter_enabled = bool(cfg.get("TOPIC_FILTER_ENABLED", False))
    allowed_topic_ids = {int(x) for x in cfg.get("ALLOWED_TOPIC_IDS", []) if str(x).strip().isdigit()}
    blocked_channel_ids = {int(x) for x in cfg.get("BLOCKED_CHANNEL_IDS", []) if str(x).strip().lstrip('-').isdigit()}
    track_group_only = bool(cfg.get("TRACK_GROUP_ONLY", False))
    backfill_enabled = bool(cfg.get("BACKFILL_ENABLED", False))

    logger.info("Starting pipeline. dry_run=%s, debug=%s", dry_run, debug)
    logger.info("Allowed channel refs=%s, allowed_group_ref=%s", allowed_channel_refs, allowed_group_ref)
    logger.info("Topic filter: enabled=%s allowed_topic_ids=%s", topic_filter_enabled, sorted(list(allowed_topic_ids)))
    logger.info("Blocked channel ids=%s", sorted(list(blocked_channel_ids)))
    logger.info("Folder mode: name=%s include_manual_when_folder=%s", allowed_folder_name or None, include_manual_when_folder)
    logger.info("Track group only=%s", track_group_only)
    logger.info("Backfill enabled=%s (pipeline handles new incoming only)", backfill_enabled)

    client = TelegramClient(session_name, api_id, api_hash, auto_reconnect=True, sequential_updates=True)

    allowed_channel_ids: Set[int] = set()
    allowed_group_id: Optional[int] = None
    target_channel_id: Optional[Union[int, str]] = None
    topic_title_map: Dict[int, str] = {}
    allowed_topic_runtime_ids: Set[int] = set(allowed_topic_ids)

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
        nonlocal topic_title_map, allowed_topic_runtime_ids
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
            logger.info("Loaded topic titles: %s", {k: topic_title_map[k] for k in sorted(topic_title_map)[:20]})
            logger.info("Resolved runtime topic ids=%s", sorted(list(allowed_topic_runtime_ids)))
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

        if track_group_only and chat_id != allowed_group_id:
            return

        if chat_id not in allowed_channel_ids and chat_id != allowed_group_id:
            return

        try:
            msg = event.message
            chat = await event.get_chat()
            chat_title = getattr(chat, "title", None) or getattr(chat, "username", None) or str(chat_id)
            topic_id = extract_topic_id(msg)

            if topic_filter_enabled and chat_id == allowed_group_id:
                if not topic_id or topic_id not in allowed_topic_runtime_ids:
                    logger.info("Dropped (topic not allowed): chat_id=%s topic_id=%s msg_id=%s", chat_id, topic_id, msg.id)
                    return

            topic_title = topic_title_map.get(topic_id) if topic_id else None
            text = msg.message or ""
            media_only = bool(msg.media) and not text.strip()

            # Ilya-specific scoring filter (applies to currently allowed Ilya topic only)
            f = classify_ilya_message(text, has_media=bool(msg.media))
            if not f["pass"]:
                logger.info("%s score=%s msg_id=%s topic_id=%s", f["reason"], f["score"], msg.id, topic_id)
                return

            type_prefix = f"[{f['type']}]\n" if f.get("type") else ""
            payload = type_prefix + format_payload(chat_title, chat_id, topic_id, text, media_only, topic_title=topic_title)

            media_kind = None
            media_bytes = None
            media_name = "media.bin"
            if msg.media:
                try:
                    if getattr(msg, "photo", None):
                        media_kind = "photo"
                        media_name = f"photo_{msg.id}.jpg"
                    elif getattr(msg, "video", None):
                        media_kind = "video"
                        media_name = f"video_{msg.id}.mp4"
                    elif getattr(msg, "voice", None):
                        media_kind = "voice"
                        media_name = f"voice_{msg.id}.ogg"
                    elif getattr(msg, "document", None):
                        media_kind = "document"
                        media_name = f"document_{msg.id}.bin"
                    if media_kind:
                        media_bytes = await client.download_media(msg, file=bytes)
                except Exception as e:
                    logger.warning("Media download failed, fallback to text only: msg_id=%s err=%s", msg.id, e)
                    media_kind = None
                    media_bytes = None

            if debug:
                logger.debug(
                    "DEBUG event: chat_id=%s title=%s message_id=%s topic_id=%s reply_to=%s is_forum=%s",
                    chat_id,
                    chat_title,
                    msg.id,
                    topic_id,
                    getattr(msg, "reply_to_msg_id", None),
                    getattr(chat, "forum", None),
                )

            if target_channel_id is None:
                logger.error("Target channel is not resolved. Skip send.")
                return

            ok = send_via_bot_api(
                bot_token,
                str(target_channel_id),
                payload,
                logger,
                dry_run=dry_run,
                media_kind=media_kind,
                media_bytes=media_bytes,
                media_name=media_name,
            )
            if ok:
                logger.info("%s score=%s msg_id=%s topic_id=%s", f["reason"], f["score"], msg.id, topic_id)
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
        nonlocal allowed_channel_ids, allowed_group_id, target_channel_id

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

        tgt = await resolve_chat_ref(client, target_channel_ref)
        if tgt is None:
            logger.warning("Cannot resolve target channel ref: %s", target_channel_ref)
            target_channel_id = str(target_channel_ref)
        else:
            if isinstance(target_channel_ref, int):
                target_channel_id = target_channel_ref
            else:
                try:
                    ent_full = await client.get_entity(target_channel_ref)
                    target_channel_id = int(get_peer_id(ent_full))
                except Exception:
                    target_channel_id = tgt

        allowed_channel_ids = resolved_channels

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
        logger.info("Resolved target_channel_id=%s", target_channel_id)

        # HARD SAFETY GUARD: never send to source channels/group
        source_ids = set(allowed_channel_ids)
        if allowed_group_id is not None:
            source_ids.add(int(allowed_group_id))
        try:
            tgt_int = int(target_channel_id) if target_channel_id is not None else None
        except Exception:
            tgt_int = None
        if tgt_int is not None and tgt_int in source_ids:
            raise RuntimeError(
                "Safety guard triggered: TARGET_CHANNEL_ID points to a source chat. "
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

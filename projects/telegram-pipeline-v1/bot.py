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
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.functions.messages import GetDialogFiltersRequest
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


def format_payload(chat_title: str, chat_id: int, topic_id: Optional[int], text: str, media_only: bool) -> str:
    if media_only:
        return f"[media message]\n[Source: {chat_title}]"

    header = [f"[Source: {chat_title}]", f"[ChatID: {chat_id}]"]
    if topic_id:
        header.append(f"[TopicID: {topic_id}]")

    body = text.strip() if text else "[empty message]"
    return "\n".join(header) + "\n\n" + body


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


def send_via_bot_api(bot_token: str, target_channel_id: str, text: str, logger: logging.Logger, dry_run: bool = False) -> bool:
    chunks = _chunk_text(text)

    if dry_run:
        logger.info("[DRY_RUN] Skip send. chunks=%s first_payload:\n%s", len(chunks), chunks[0])
        return True

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    for idx, chunk in enumerate(chunks, start=1):
        payload = {
            "chat_id": target_channel_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }

        sent = False
        for attempt in range(1, 4):
            try:
                r = requests.post(url, json=payload, timeout=20)
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
                sent = True
                break
            except requests.RequestException as e:
                logger.error("Bot API send error chunk %s/%s attempt %s/3: %s", idx, len(chunks), attempt, e)
                time.sleep(1.5 * attempt)

        if not sent:
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

    logger.info("Starting pipeline. dry_run=%s, debug=%s", dry_run, debug)
    logger.info("Allowed channel refs=%s, allowed_group_ref=%s", allowed_channel_refs, allowed_group_ref)
    logger.info("Topic filter: enabled=%s allowed_topic_ids=%s", topic_filter_enabled, sorted(list(allowed_topic_ids)))
    logger.info("Blocked channel ids=%s", sorted(list(blocked_channel_ids)))
    logger.info("Folder mode: name=%s include_manual_when_folder=%s", allowed_folder_name or None, include_manual_when_folder)

    client = TelegramClient(session_name, api_id, api_hash, auto_reconnect=True, sequential_updates=True)

    allowed_channel_ids: Set[int] = set()
    allowed_group_id: Optional[int] = None
    target_channel_id: Optional[Union[int, str]] = None

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

    @client.on(events.NewMessage(incoming=True))
    async def on_new_message(event):
        chat_id = int(event.chat_id)

        if chat_id in blocked_channel_ids:
            logger.warning("Blocked channel skipped: chat_id=%s message_id=%s", chat_id, getattr(event.message, 'id', None))
            return

        if chat_id not in allowed_channel_ids and chat_id != allowed_group_id:
            return

        try:
            msg = event.message
            chat = await event.get_chat()
            chat_title = getattr(chat, "title", None) or getattr(chat, "username", None) or str(chat_id)
            topic_id = extract_topic_id(msg)

            # topic filter scaffold (off by default)
            if topic_filter_enabled and chat_id == allowed_group_id:
                if not topic_id or topic_id not in allowed_topic_ids:
                    logger.debug("Topic filtered out: chat_id=%s topic_id=%s", chat_id, topic_id)
                    return

            text = msg.message or ""
            media_only = bool(msg.media) and not text.strip()
            payload = format_payload(chat_title, chat_id, topic_id, text, media_only)

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

            ok = send_via_bot_api(bot_token, str(target_channel_id), payload, logger, dry_run=dry_run)
            if ok:
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

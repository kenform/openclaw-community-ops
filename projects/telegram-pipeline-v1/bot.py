#!/usr/bin/env python3
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RpcError

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


def send_via_bot_api(bot_token: str, target_channel_id: str, text: str, logger: logging.Logger, dry_run: bool = False) -> bool:
    if dry_run:
        logger.info("[DRY_RUN] Skip send. Payload:\n%s", text)
        return True

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": target_channel_id,
        "text": text,
        "disable_web_page_preview": True,
    }

    for attempt in range(1, 4):
        try:
            r = requests.post(url, json=payload, timeout=20)
            if r.status_code == 429:
                retry_after = r.json().get("parameters", {}).get("retry_after", 2)
                logger.warning("Bot API rate limit. retry_after=%s", retry_after)
                time.sleep(retry_after)
                continue

            r.raise_for_status()
            data = r.json()
            if not data.get("ok"):
                logger.error("Bot API responded ok=false: %s", data)
                return False
            return True
        except requests.RequestException as e:
            logger.error("Bot API send error attempt %s/3: %s", attempt, e)
            time.sleep(1.5 * attempt)

    return False


def normalize_ids(raw_ids):
    return {int(x) for x in raw_ids}


def main() -> None:
    cfg = load_json(CONFIG_PATH, default={})

    required = [
        "TELEGRAM_API_ID",
        "TELEGRAM_API_HASH",
        "SESSION_NAME",
        "BOT_TOKEN",
        "TARGET_CHANNEL_ID",
        "ALLOWED_CHANNEL_IDS",
        "ALLOWED_GROUP_ID",
        "DRY_RUN",
    ]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise SystemExit(f"Missing config keys: {', '.join(missing)}")

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
    target_channel_id = str(cfg["TARGET_CHANNEL_ID"])
    allowed_channels = normalize_ids(cfg["ALLOWED_CHANNEL_IDS"])
    allowed_group_id = int(cfg["ALLOWED_GROUP_ID"])
    dry_run = bool(cfg["DRY_RUN"])

    logger.info("Starting pipeline. dry_run=%s, debug=%s", dry_run, debug)
    logger.info("Allowed channels=%s, allowed_group=%s", sorted(allowed_channels), allowed_group_id)

    client = TelegramClient(session_name, api_id, api_hash, auto_reconnect=True, sequential_updates=True)

    should_stop = {"value": False}

    def _shutdown(*_args):
        should_stop["value"] = True
        logger.info("Shutdown signal received")

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    @client.on(events.NewMessage(incoming=True))
    async def on_new_message(event):
        chat_id = int(event.chat_id)

        if chat_id not in allowed_channels and chat_id != allowed_group_id:
            return

        try:
            msg = event.message
            chat = await event.get_chat()
            chat_title = getattr(chat, "title", None) or getattr(chat, "username", None) or str(chat_id)
            topic_id = extract_topic_id(msg)

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

            ok = send_via_bot_api(bot_token, target_channel_id, payload, logger, dry_run=dry_run)
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
        except RpcError as e:
            logger.error("Telethon RPC error: %s", e)
        except Exception as e:
            logger.exception("Unhandled pipeline error: %s", e)

    async def runner():
        await client.start()
        me = await client.get_me()
        logger.info("Reader authorized as %s", getattr(me, "username", me.id))

        while not should_stop["value"]:
            if not client.is_connected():
                logger.warning("Client disconnected. Attempting reconnect...")
                try:
                    await client.connect()
                except Exception as e:
                    logger.error("Reconnect failed: %s", e)
            await client.run_until_disconnected()

    try:
        with client:
            client.loop.run_until_complete(runner())
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        raise


if __name__ == "__main__":
    main()

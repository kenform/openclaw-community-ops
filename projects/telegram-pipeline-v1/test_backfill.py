#!/usr/bin/env python3
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from telethon import TelegramClient

from bot import (
    extract_topic_id,
    classify_artur_main,
    parse_artur_signal,
    classify_main_ilya_message,
    parse_ilya_signal,
    parse_generic_signal,
    load_ilya_rules,
    has_tradingview_link,
)
from behavior_layer import apply_behavior_profile, update_context

BASE_DIR = Path(__file__).resolve().parent


def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def detect_media_kind(msg) -> Optional[str]:
    if getattr(msg, "photo", None):
        return "photo"
    if getattr(msg, "video", None):
        return "video"
    if getattr(msg, "voice", None):
        return "voice"
    if getattr(msg, "document", None):
        return "document"
    if getattr(msg, "media", None):
        return "media"
    return None


def fmt_bool(v: bool) -> str:
    return "Y" if v else "N"


def print_row(trader: str, msg_id: int, state: str, main: bool, signal: bool, has_media: bool, reasons: List[str]) -> None:
    reason_text = ",".join(reasons[:4])
    print(f"{trader:<8} | {msg_id:<10} | {state:<12} | {fmt_bool(main):<4} | {fmt_bool(signal):<6} | {fmt_bool(has_media):<9} | {reason_text}")


async def fetch_source_messages(client: TelegramClient, src: Dict[str, Any], limit: int = 50) -> List[Any]:
    chat_id = src["chat_id"]
    stype = src.get("type", "channel")

    if stype == "topic":
        topic_ids = set(src.get("topic_ids") or [])
        bucket: Dict[int, Any] = {}
        had_topic_error = False

        for tid in topic_ids:
            try:
                async for msg in client.iter_messages(chat_id, limit=limit, reply_to=tid):
                    if msg and msg.id:
                        bucket[msg.id] = msg
            except Exception:
                had_topic_error = True

        # Fallback: scan recent chat history and filter by extracted topic id.
        if had_topic_error or not bucket:
            async for msg in client.iter_messages(chat_id, limit=400):
                mid = extract_topic_id(msg)
                if mid in topic_ids and msg and msg.id:
                    bucket[msg.id] = msg
                if len(bucket) >= limit:
                    break

        items = sorted(bucket.values(), key=lambda m: m.id, reverse=True)
        return items[:limit]

    out: List[Any] = []
    async for msg in client.iter_messages(chat_id, limit=limit):
        out.append(msg)
    return out


async def main() -> None:
    cfg = load_json(BASE_DIR / "config.json", {})
    src_cfg = load_json(BASE_DIR / "sources.json", {"sources": []})
    trader_cfg = load_json(BASE_DIR / "traders.json", {"traders": {}, "tradingview_patterns": ["tradingview.com"]})

    api_id = int(cfg["TELEGRAM_API_ID"])
    api_hash = str(cfg["TELEGRAM_API_HASH"])
    session_name = str(cfg.get("SESSION_NAME") or (BASE_DIR / "reader_session"))

    logger = logging.getLogger("test_backfill")
    logger.setLevel(logging.INFO)
    rules = load_ilya_rules(cfg, logger)

    callbacks = {
        "classify_artur_main": classify_artur_main,
        "parse_artur_signal": parse_artur_signal,
        "classify_main_ilya_message": classify_main_ilya_message,
        "parse_ilya_signal": parse_ilya_signal,
        "parse_generic_signal": parse_generic_signal,
        "rules": rules,
        "ilya_main_filter_enabled": bool(cfg.get("ILYA_MAIN_FILTER_ENABLED", True)),
    }

    tv_patterns = trader_cfg.get("tradingview_patterns", ["tradingview.com"])
    trader_profiles = trader_cfg.get("traders", {})
    recent_context: Dict[str, List[Dict[str, Any]]] = {}

    print("dry_run=True (hardcoded), nothing will be sent")
    print("trader   | msg_id     | state        | main | signal | has_media | reasons")
    print("-" * 110)

    async with TelegramClient(session_name, api_id, api_hash) as client:
        for src in src_cfg.get("sources", []):
            trader_id = (src.get("trader") or "unknown").lower()
            messages = await fetch_source_messages(client, src, limit=50)

            for msg in messages:
                text = (getattr(msg, "message", None) or "").strip()
                has_media = bool(getattr(msg, "media", None))
                media_kind = detect_media_kind(msg)
                tv_link = has_tradingview_link(text, tv_patterns)

                update_context(recent_context, trader_id, {
                    "msg_id": msg.id,
                    "text": text,
                    "has_media": has_media,
                    "topic_id": extract_topic_id(msg),
                })

                threshold = int((trader_profiles.get(trader_id) or {}).get("signal_threshold", 6))
                ctx_window = recent_context.get(trader_id, [])

                decision = apply_behavior_profile(
                    trader_id=trader_id,
                    text=text,
                    has_media=has_media,
                    media_kind=media_kind,
                    context_window=ctx_window,
                    callbacks=callbacks,
                    tv_link=tv_link,
                    signal_threshold=threshold,
                )

                print_row(
                    trader_id,
                    msg.id,
                    decision.get("state_type", ""),
                    bool(decision.get("main_pass")),
                    bool(decision.get("signal_pass")),
                    has_media,
                    decision.get("debug_reasons", []),
                )


if __name__ == "__main__":
    asyncio.run(main())

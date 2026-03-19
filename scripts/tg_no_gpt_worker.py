#!/usr/bin/env python3
import asyncio
import hashlib
import json
import re
import sys
import time
from pathlib import Path

from telethon import TelegramClient


def norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def text_fp(s: str) -> str:
    return hashlib.sha1(norm_text(s).encode("utf-8", "ignore")).hexdigest()


async def run(config_path: str):
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    cleanup = cfg["cleanup"]

    env_path = Path("/home/openclawuser/userbot2/config.env")
    env = {}
    for ln in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in ln and not ln.strip().startswith("#"):
            k, v = ln.split("=", 1)
            env[k.strip()] = v.strip()

    api_id = int(env["TELEGRAM_API_ID"])
    api_hash = env["TELEGRAM_API_HASH"]

    client = TelegramClient("/home/openclawuser/userbot2/session", api_id, api_hash)
    await client.connect()
    me = await client.get_me()
    my_id = getattr(me, "id", None)

    dialogs = []
    async for d in client.iter_dialogs(limit=600):
        if d.is_group:
            dialogs.append(d)

    target_names = set((x or "").strip().lower() for x in cleanup.get("groups", []))
    excl_contains = [x.lower() for x in cleanup.get("exclude_name_contains", [])]
    excl_exact = set((x or "").strip().lower() for x in cleanup.get("exclude_exact", []))

    def group_allowed(name: str) -> bool:
        low = (name or "").strip().lower()
        if not low:
            return False
        if low in excl_exact:
            return False
        if any(x in low for x in excl_contains):
            return False
        return (not target_names) or (low in target_names)

    candidates = [d for d in dialogs if group_allowed(d.name or "")]
    # If same group name appears multiple times, prefer megagroup/supergroup entities.
    by_name = {}
    for d in candidates:
        low = (d.name or "").strip().lower()
        ent = d.entity
        score = 0
        if bool(getattr(ent, "megagroup", False)):
            score += 2
        if bool(getattr(ent, "forum", False)):
            score += 1
        prev = by_name.get(low)
        if prev is None or score > prev[0]:
            by_name[low] = (score, d)
    selected = [v[1] for v in by_name.values()]

    report = {
        "ts": int(time.time()),
        "mode": "no_gpt_cleanup_worker",
        "selected_groups": len(selected),
        "groups": [],
        "summary": {},
    }

    limit = int(cleanup.get("limit_per_group", 260))
    del_service = bool(cleanup.get("delete_service", True))
    del_empty = bool(cleanup.get("delete_empty", True))
    dedupe = bool(cleanup.get("dedupe_exact_text", True))

    total_deleted = total_failed = total_scanned = 0

    for d in selected:
        st = {
            "name": d.name,
            "chat_id": d.id,
            "scanned": 0,
            "service_candidates": 0,
            "empty_candidates": 0,
            "dup_candidates": 0,
            "deleted": 0,
            "failed": 0,
        }
        delete_ids = []
        seen_text = set()

        async for m in client.iter_messages(d.entity, limit=limit):
            st["scanned"] += 1
            total_scanned += 1

            txt = (m.raw_text or "").strip()
            has_media = bool(m.media)
            is_service = bool(getattr(m, "action", None))
            is_mine = bool(getattr(m, "out", False)) or (getattr(m, "sender_id", None) == my_id)

            if del_service and is_service:
                st["service_candidates"] += 1
                delete_ids.append(m.id)
                continue

            if del_empty and (not txt) and (not has_media):
                st["empty_candidates"] += 1
                delete_ids.append(m.id)
                continue

            if dedupe and txt and is_mine:
                fp = text_fp(txt)
                if fp in seen_text:
                    st["dup_candidates"] += 1
                    delete_ids.append(m.id)
                else:
                    seen_text.add(fp)

        for i in range(0, len(delete_ids), 100):
            chunk = delete_ids[i : i + 100]
            try:
                await client.delete_messages(d.entity, chunk)
                st["deleted"] += len(chunk)
                total_deleted += len(chunk)
            except Exception:
                st["failed"] += len(chunk)
                total_failed += len(chunk)

        report["groups"].append(st)

    report["summary"] = {
        "groups_processed": len(report["groups"]),
        "scanned_total": total_scanned,
        "deleted_total": total_deleted,
        "failed_total": total_failed,
    }

    await client.disconnect()
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: tg_no_gpt_worker.py <config_path>")
        raise SystemExit(2)
    rep = asyncio.run(run(sys.argv[1]))
    print(json.dumps(rep, ensure_ascii=False))

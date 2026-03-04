#!/usr/bin/env bash
set -euo pipefail

TS_UTC="$(date -u +'%Y-%m-%d %H:%M:%S UTC')"
OUT_DIR="/home/openclawuser/.openclaw/workspace/tmp/userbot-audit"
OUT_FILE="$OUT_DIR/weekly-$(date -u +%F).md"
BOT_DIR="/home/openclawuser/userbot"
CFG="$BOT_DIR/digest_config.json"
LOG="$BOT_DIR/userbot_events.jsonl"
mkdir -p "$OUT_DIR"

active="$(systemctl --user is-active userbot 2>/dev/null || true)"
compile="ok"
python3 -m py_compile "$BOT_DIR/bot.py" >/dev/null 2>&1 || compile="fail"

channels_total=0
duplicates=0
python3 - <<'PY' > /tmp/userbot_audit_stats.txt
import json
from collections import Counter
from pathlib import Path
cfg=Path('/home/openclawuser/userbot/digest_config.json')
chs=[]
if cfg.exists():
    d=json.loads(cfg.read_text(encoding='utf-8'))
    chs=[str(x).strip().lstrip('@').lower() for x in d.get('channels',[]) if str(x).strip()]
c=Counter(chs)
dups=sum(v-1 for v in c.values() if v>1)
print(len(chs))
print(dups)
PY
channels_total="$(sed -n '1p' /tmp/userbot_audit_stats.txt)"
duplicates="$(sed -n '2p' /tmp/userbot_audit_stats.txt)"

err24=0
err7d=0
if [[ -f "$LOG" ]]; then
  err24="$(tail -n 3000 "$LOG" | egrep -ic 'error|fail|exception|flood|cooldown' || true)"
  err7d="$(tail -n 30000 "$LOG" | egrep -ic 'error|fail|exception|flood|cooldown' || true)"
fi

cat > "$OUT_FILE" <<MD
# Userbot Weekly Audit
- Timestamp: $TS_UTC
- Service active: $active
- bot.py compile: $compile
- Digest channels total: $channels_total
- Duplicate channels in .dl: $duplicates
- Error-like events (recent window):
  - ~24h: $err24
  - ~7d sample: $err7d

## Safety / Anti-block policy
- Safe mode should stay ON
- AI digest should stay OFF unless upstream stable
- Join commands should be rate-limited (already enabled)
- Digest runs in batches + rotation (already enabled)

## Recommended thresholds
- If 24h errors > 40: review noisy channels and mute via .dl_mute
- If duplicates > 0: run cleanup (dedup .dl)
- If service not active or compile fail: immediate manual intervention
MD

# Optional quick alert to Saved Messages (only if failures)
if [[ "$active" != "active" || "$compile" != "ok" ]]; then
  /home/openclawuser/userbot/.venv/bin/python - <<'PY' || true
import asyncio
from pathlib import Path
from telethon import TelegramClient

base=Path('/home/openclawuser/userbot')
E={}
for ln in (base/'config.env').read_text(encoding='utf-8').splitlines():
    if '=' in ln and not ln.strip().startswith('#'):
        k,v=ln.split('=',1); E[k.strip()]=v.strip()
api_id=int(E['TELEGRAM_API_ID']); api_hash=E['TELEGRAM_API_HASH']
msg='⚠️ Weekly userbot audit detected issue. Check report: /home/openclawuser/.openclaw/workspace/tmp/userbot-audit/'

async def main():
    c=TelegramClient(str(base/'session'), api_id, api_hash)
    await c.start()
    await c.send_message('me', msg)
    await c.disconnect()
asyncio.run(main())
PY
fi

echo "$OUT_FILE"

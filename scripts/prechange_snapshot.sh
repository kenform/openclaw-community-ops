#!/usr/bin/env bash
set -euo pipefail
TS=$(date -u +"%Y%m%d-%H%M%S")
OUT="$HOME/.openclaw/backups/prechange"
mkdir -p "$OUT"
cp -a "$HOME/userbot/bot.py" "$OUT/bot.py.$TS"
cp -a "$HOME/userbot/config.env" "$OUT/config.env.$TS" 2>/dev/null || true
ls -1t "$OUT"/bot.py.* 2>/dev/null | tail -n +11 | xargs -r rm -f
ls -1t "$OUT"/config.env.* 2>/dev/null | tail -n +11 | xargs -r rm -f
echo "$OUT"

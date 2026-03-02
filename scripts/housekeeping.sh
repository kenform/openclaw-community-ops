#!/usr/bin/env bash
set -euo pipefail

# Lightweight housekeeping for OpenClaw/userbot host
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_DIR="$HOME/.openclaw/workspace/tmp"
LOG_FILE="$LOG_DIR/housekeeping.log"
mkdir -p "$LOG_DIR"

echo "[$NOW] housekeeping start" >> "$LOG_FILE"

# 1) userbot tmp: remove files older than 3 days
find "$HOME/userbot/tmp" -type f -mtime +3 -print -delete 2>/dev/null >> "$LOG_FILE" || true

# 2) keep only 3 latest bot backups
if compgen -G "$HOME/userbot/bot.py.bak_*" > /dev/null; then
  ls -1t "$HOME"/userbot/bot.py.bak_* | tail -n +4 | xargs -r rm -f
fi

# 3) inbound media older than 14 days
find "$HOME/.openclaw/media/inbound" -type f -mtime +14 -print -delete 2>/dev/null >> "$LOG_FILE" || true

# 4) local temp files older than 7 days
find /tmp/openclaw -type f -mtime +7 -print -delete 2>/dev/null >> "$LOG_FILE" || true

# 5) trim log file itself
if [ -f "$LOG_FILE" ]; then
  tail -n 400 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

# 6) snapshot disk and memory
{
  echo "--- usage snapshot ---"
  df -h / | tail -n 1
  free -h | sed -n '2p'
  echo "[$NOW] housekeeping done"
  echo
} >> "$LOG_FILE"

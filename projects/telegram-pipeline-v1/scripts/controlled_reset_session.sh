#!/usr/bin/env bash
set -euo pipefail

# Controlled reset for pipeline session (run in quiet window)
SERVICE="telegram-pipeline-v1.service"
BASE="/home/openclawuser/.openclaw/workspace/projects/telegram-pipeline-v1"
SESSION="$BASE/reader_session.session"
BACKUP_DIR="$BASE/session_backups"
TS=$(date -u +%Y%m%dT%H%M%SZ)

mkdir -p "$BACKUP_DIR"

echo "[1/5] stop $SERVICE"
systemctl --user stop "$SERVICE"

echo "[2/5] backup session"
if [[ -f "$SESSION" ]]; then
  cp -a "$SESSION" "$BACKUP_DIR/reader_session.session.$TS.bak"
fi

# Optional destructive reset (uncomment only when authorized)
# rm -f "$SESSION"

echo "[3/5] start $SERVICE"
systemctl --user start "$SERVICE"

echo "[4/5] status"
systemctl --user --no-pager status "$SERVICE" | sed -n '1,25p'

echo "[5/5] done"

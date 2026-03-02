#!/usr/bin/env bash
set -euo pipefail

# Smart local backup for OpenClaw stack
# - Creates timestamped tar.zst snapshot
# - Keeps manifests + quick metadata
# - Applies retention (daily + weekly)

TS=$(date -u +"%Y%m%d-%H%M%S")
DAY=$(date -u +"%Y-%m-%d")
DOW=$(date -u +"%u") # 1..7

BASE="$HOME/.openclaw/backups"
DAILY="$BASE/daily"
WEEKLY="$BASE/weekly"
META="$BASE/meta"
TMP="$BASE/.tmp-$TS"
LOG="$BASE/backup.log"

mkdir -p "$DAILY" "$WEEKLY" "$META" "$TMP"

ARCHIVE_NAME="openclaw-backup-$TS.tar.zst"
ARCHIVE_PATH="$DAILY/$ARCHIVE_NAME"

# Sources (curated to avoid junk)
SRC_WORKSPACE="$HOME/.openclaw/workspace"
SRC_VAULT="$HOME/vault"
SRC_USERBOT="$HOME/userbot"
SRC_CONFIG="$HOME/.openclaw/openclaw.json"
SRC_SYSTEMD="$HOME/.config/systemd/user"

# Build staging list using rsync for sane excludes
mkdir -p "$TMP/workspace" "$TMP/vault" "$TMP/userbot" "$TMP/config" "$TMP/systemd"

rsync -a --delete \
  --exclude '.git/objects/pack/*.pack' \
  --exclude 'node_modules/' \
  --exclude '.whisper-venv/' \
  "$SRC_WORKSPACE/" "$TMP/workspace/"

rsync -a --delete "$SRC_VAULT/" "$TMP/vault/"

rsync -a --delete \
  --exclude '.venv/' \
  --exclude 'tmp/' \
  --exclude '__pycache__/' \
  "$SRC_USERBOT/" "$TMP/userbot/"

[ -f "$SRC_CONFIG" ] && cp -a "$SRC_CONFIG" "$TMP/config/openclaw.json" || true
[ -d "$SRC_SYSTEMD" ] && rsync -a "$SRC_SYSTEMD/" "$TMP/systemd/" || true

# Metadata
{
  echo "timestamp_utc=$TS"
  echo "day_utc=$DAY"
  echo "host=$(hostname)"
  echo "kernel=$(uname -srmo)"
  echo "disk_root=$(df -h / | tail -n1)"
  echo "mem=$(free -h | sed -n '2p')"
} > "$TMP/BACKUP_META.txt"

# Archive with zstd (fast-ish)
( cd "$TMP" && tar --zstd -cf "$ARCHIVE_PATH" . )
sha256sum "$ARCHIVE_PATH" > "$ARCHIVE_PATH.sha256"
ln -sfn "$ARCHIVE_PATH" "$DAILY/latest.tar.zst"
ln -sfn "$ARCHIVE_PATH.sha256" "$DAILY/latest.tar.zst.sha256"

# Weekly pin on Monday (UTC)
if [ "$DOW" = "1" ]; then
  cp -a "$ARCHIVE_PATH" "$WEEKLY/$ARCHIVE_NAME"
  cp -a "$ARCHIVE_PATH.sha256" "$WEEKLY/$ARCHIVE_NAME.sha256"
fi

# Retention: keep 14 daily + 8 weekly
ls -1t "$DAILY"/openclaw-backup-*.tar.zst 2>/dev/null | tail -n +15 | xargs -r rm -f
ls -1t "$DAILY"/openclaw-backup-*.tar.zst.sha256 2>/dev/null | tail -n +15 | xargs -r rm -f
ls -1t "$WEEKLY"/openclaw-backup-*.tar.zst 2>/dev/null | tail -n +9 | xargs -r rm -f
ls -1t "$WEEKLY"/openclaw-backup-*.tar.zst.sha256 2>/dev/null | tail -n +9 | xargs -r rm -f

# Update latest summary
{
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] OK $ARCHIVE_PATH"
} >> "$LOG"
tail -n 400 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"

rm -rf "$TMP"
echo "$ARCHIVE_PATH"

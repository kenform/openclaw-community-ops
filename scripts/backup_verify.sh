#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/.openclaw/backups"
DAILY="$BASE/daily"
TESTDIR="$BASE/verify-tmp"
LATEST_LINK="$DAILY/latest.tar.zst"

if [ ! -L "$LATEST_LINK" ] && [ ! -f "$LATEST_LINK" ]; then
  echo "No latest backup found" >&2
  exit 1
fi

ARCHIVE=$(readlink -f "$LATEST_LINK")
SUM_FILE="$ARCHIVE.sha256"

sha256sum -c "$SUM_FILE"

rm -rf "$TESTDIR"
mkdir -p "$TESTDIR"
# smoke extract one critical file (avoid pipefail false-negatives)
LIST_FILE="$TESTDIR/archive.list"
tar --zstd -tf "$ARCHIVE" > "$LIST_FILE"
if grep -q "^\./config/openclaw.json$" "$LIST_FILE"; then
  tar --zstd -xf "$ARCHIVE" -C "$TESTDIR" ./config/openclaw.json
  [ -s "$TESTDIR/config/openclaw.json" ] || { echo "restore smoke failed"; exit 2; }
else
  echo "warning: config/openclaw.json missing in backup" >&2
fi

# list top-level payload
printf "verified archive: %s\n" "$ARCHIVE"
tar --zstd -tf "$ARCHIVE" | sed -n '1,20p'
rm -rf "$TESTDIR"

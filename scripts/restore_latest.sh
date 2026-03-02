#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/.openclaw/backups/daily"
LATEST_LINK="$BASE/latest.tar.zst"
RESTORE_ROOT="$HOME/.openclaw/restore"
TS=$(date -u +"%Y%m%d-%H%M%S")
OUT="$RESTORE_ROOT/restore-$TS"
MODE="preview"
AUTO_YES=0

usage(){
  cat <<EOF
Usage: $0 [--apply] [--yes]
  --apply   perform restore into live paths (careful)
  --yes     skip confirmation prompt (only with --apply)
Default: preview extraction only (safe)
EOF
}

for a in "$@"; do
  case "$a" in
    --apply) MODE="apply" ;;
    --yes) AUTO_YES=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $a"; usage; exit 1 ;;
  esac
done

[ -f "$LATEST_LINK" ] || { echo "No latest backup found: $LATEST_LINK"; exit 1; }
ARCHIVE=$(readlink -f "$LATEST_LINK")
SUM="$ARCHIVE.sha256"

mkdir -p "$OUT"
sha256sum -c "$SUM"

tar --zstd -xf "$ARCHIVE" -C "$OUT"
echo "Preview extracted to: $OUT"

echo "Top-level extracted:"
find "$OUT" -maxdepth 2 -type d | sed -n '1,40p'

if [ "$MODE" = "preview" ]; then
  echo "Preview mode only. Nothing applied."
  exit 0
fi

if [ "$AUTO_YES" -ne 1 ]; then
  echo "About to APPLY restore from: $ARCHIVE"
  echo "Targets: ~/.openclaw/workspace, ~/vault, ~/userbot, ~/.openclaw/openclaw.json, ~/.config/systemd/user"
  read -r -p "Type YES to continue: " x
  [ "$x" = "YES" ] || { echo "Aborted."; exit 1; }
fi

# Apply with rsync for controlled overwrite (preserve permissions)
rsync -a --delete "$OUT/workspace/" "$HOME/.openclaw/workspace/"
rsync -a --delete "$OUT/vault/" "$HOME/vault/"
rsync -a --delete "$OUT/userbot/" "$HOME/userbot/"
[ -f "$OUT/config/openclaw.json" ] && cp -a "$OUT/config/openclaw.json" "$HOME/.openclaw/openclaw.json" || true
[ -d "$OUT/systemd" ] && rsync -a "$OUT/systemd/" "$HOME/.config/systemd/user/" || true

systemctl --user daemon-reload || true
systemctl --user restart openclaw-gateway.service || true
systemctl --user restart userbot.service || true

echo "Restore applied from $ARCHIVE"

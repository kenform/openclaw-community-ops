#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="$HOME/.openclaw/workspace/tmp/maintenance"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/disk-weekly-$(date +%F).log"
ALERT_FILE="$LOG_DIR/ALERTS.log"
ALERT_THRESHOLD="${ALERT_THRESHOLD:-15}"

{
  echo "=== Weekly disk maintenance: $(date -Is) ==="
  echo "\n[Disk usage]"
  df -h / /home

  AVAIL_PCT=$(df --output=pcent / | tail -1 | tr -dc '0-9')
  FREE_PCT=$((100 - AVAIL_PCT))
  echo "Free space: ${FREE_PCT}% (threshold: ${ALERT_THRESHOLD}%)"
  if (( FREE_PCT < ALERT_THRESHOLD )); then
    ALERT_MSG="ALERT $(date -Is): low disk space on / => ${FREE_PCT}% free (< ${ALERT_THRESHOLD}%)"
    echo "$ALERT_MSG"
    echo "$ALERT_MSG" >> "$ALERT_FILE"
    command -v logger >/dev/null 2>&1 && logger -t openclaw-maintenance "$ALERT_MSG" || true
  fi

  echo "\n[Top dirs in /home/openclawuser]"
  du -h --max-depth=2 "$HOME" 2>/dev/null | sort -hr | head -n 25

  if [[ "${AUTO_CLEAN:-0}" == "1" ]]; then
    echo "\n[Cleanup mode ON]"

    # Old temp transcriptions / scratch files
    find "$HOME/.openclaw/workspace/tmp" -type f -mtime +14 -print -delete 2>/dev/null || true

    # Old TTS temp artifacts
    find /tmp/openclaw -maxdepth 2 -type f -name 'voice-*.mp3' -mtime +14 -print -delete 2>/dev/null || true

    # Pip cache can grow large; safe to purge old cache
    if command -v pip >/dev/null 2>&1; then
      pip cache purge >/dev/null 2>&1 || true
      echo "pip cache purge: done"
    fi

    # NPM cache cleanup (non-destructive verify)
    if command -v npm >/dev/null 2>&1; then
      npm cache verify >/dev/null 2>&1 || true
      echo "npm cache verify: done"
    fi
  else
    echo "\n[Cleanup mode OFF] Set AUTO_CLEAN=1 to enable cleanup actions]"
  fi

  echo "\n=== Done ==="
} | tee "$LOG_FILE"

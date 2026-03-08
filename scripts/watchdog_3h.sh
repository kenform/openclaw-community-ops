#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="$HOME/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/watchdog-3h-$(date -u +%Y%m%dT%H%M%SZ).log"

services=(
  "openclaw-gateway.service"
  "userbot.service"
  "telegram-pipeline-v1.service"
  "psybot-api.service"
)

check_and_fix() {
  local svc="$1"
  local active sub
  active=$(systemctl --user show "$svc" -p ActiveState --value || echo "unknown")
  sub=$(systemctl --user show "$svc" -p SubState --value || echo "unknown")

  echo "[$(date -u +%FT%TZ)] $svc active=$active sub=$sub" | tee -a "$LOG_FILE"

  if [[ "$active" != "active" ]] || [[ "$sub" == "failed" ]] || [[ "$sub" == "dead" ]] || [[ "$sub" == "stop-sigterm" ]] || [[ "$sub" == "deactivating" ]]; then
    echo "[$(date -u +%FT%TZ)] repair $svc -> restart" | tee -a "$LOG_FILE"
    systemctl --user reset-failed "$svc" || true
    systemctl --user restart "$svc" || true
    sleep 2
    active=$(systemctl --user show "$svc" -p ActiveState --value || echo "unknown")
    sub=$(systemctl --user show "$svc" -p SubState --value || echo "unknown")
    echo "[$(date -u +%FT%TZ)] post-restart $svc active=$active sub=$sub" | tee -a "$LOG_FILE"
  fi
}

echo "[$(date -u +%FT%TZ)] watchdog started (3h, every 15m)" | tee -a "$LOG_FILE"

for i in {1..12}; do
  echo "[$(date -u +%FT%TZ)] cycle=$i/12" | tee -a "$LOG_FILE"
  for svc in "${services[@]}"; do
    check_and_fix "$svc"
  done

  # quick health/resource snapshot
  "$HOME/.nvm/versions/node/v22.22.0/bin/openclaw" health --json | sed -n '1,8p' | tr '\n' ' ' | sed 's/$/\n/' | tee -a "$LOG_FILE" || true
  free -h | sed -n '1,3p' | tr '\n' ' ' | sed 's/$/\n/' | tee -a "$LOG_FILE"

  if [[ "$i" -lt 12 ]]; then
    sleep 900
  fi
done

echo "[$(date -u +%FT%TZ)] watchdog completed" | tee -a "$LOG_FILE"
echo "$LOG_FILE"

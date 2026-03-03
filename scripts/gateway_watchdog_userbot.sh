#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="$HOME/.openclaw/workspace/tmp/watchdog"
ALERT_FILE="$HOME/.openclaw/workspace/tmp/selfheal_alert.json"
mkdir -p "$STATE_DIR"

FAIL_COUNT_FILE="$STATE_DIR/fail_count"
LAST_ALERT_FILE="$STATE_DIR/last_alert_ts"
COOLDOWN_SEC=900
MAX_FAILS=3

fail_count=0
[[ -f "$FAIL_COUNT_FILE" ]] && fail_count=$(cat "$FAIL_COUNT_FILE" 2>/dev/null || echo 0)

if openclaw gateway status >/tmp/gateway_watchdog_status.txt 2>&1; then
  echo 0 > "$FAIL_COUNT_FILE"
  exit 0
fi

fail_count=$((fail_count + 1))
echo "$fail_count" > "$FAIL_COUNT_FILE"

if (( fail_count < MAX_FAILS )); then
  exit 0
fi

now=$(date +%s)
last=0
[[ -f "$LAST_ALERT_FILE" ]] && last=$(cat "$LAST_ALERT_FILE" 2>/dev/null || echo 0)

if (( now - last < COOLDOWN_SEC )); then
  exit 0
fi

# try self-heal
openclaw gateway restart >/tmp/gateway_watchdog_restart.txt 2>&1 || true

# verify after restart
sleep 3
if openclaw gateway status >/tmp/gateway_watchdog_status_after.txt 2>&1; then
  level="warning"
  msg="Gateway был недоступен, выполнен авто-restart, сервис восстановлен."
else
  level="critical"
  msg="Gateway недоступен после авто-restart. Нужна ручная проверка."
fi

cat > "$ALERT_FILE" <<JSON
{
  "ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "level": "$level",
  "service": "openclaw-gateway",
  "message": "$msg",
  "sent": false
}
JSON

echo "$now" > "$LAST_ALERT_FILE"

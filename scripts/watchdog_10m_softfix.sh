#!/usr/bin/env bash
set -u

INTERVAL_SEC="${INTERVAL_SEC:-600}"
LOG_DIR="/home/openclawuser/.openclaw/workspace/logs"
ALERT_LOG="$LOG_DIR/watchdog-alerts.log"
STATE_LOG="$LOG_DIR/watchdog-state.log"
OPENCLAW_BIN="/home/openclawuser/.nvm/versions/node/v22.22.0/bin/openclaw"

mkdir -p "$LOG_DIR"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log_state() { echo "[$(ts)] $*" >> "$STATE_LOG"; }
log_alert() { echo "[$(ts)] ALERT: $*" >> "$ALERT_LOG"; }

check_once() {
  local issues=0

  # 1) ensure openclaw CLI alias exists (soft-fix, no restarts)
  if [[ ! -x /home/openclawuser/.local/bin/openclaw ]]; then
    mkdir -p /home/openclawuser/.local/bin
    ln -sfn "$OPENCLAW_BIN" /home/openclawuser/.local/bin/openclaw
    log_state "softfix: restored ~/.local/bin/openclaw symlink"
  fi

  # 2) userbot service health
  if ! systemctl --user is-active --quiet userbot.service; then
    issues=$((issues+1))
    log_alert "userbot.service is NOT active. restart required -> approval needed"
  fi

  # 3) gateway service health
  if ! systemctl --user is-active --quiet openclaw-gateway.service; then
    issues=$((issues+1))
    log_alert "openclaw-gateway.service is NOT active. restart required -> approval needed"
  fi

  # 4) gateway probe (non-invasive)
  if ! "$OPENCLAW_BIN" gateway probe --json >/tmp/watchdog_probe.json 2>/tmp/watchdog_probe.err; then
    issues=$((issues+1))
    log_alert "gateway probe command failed (non-invasive check). see /tmp/watchdog_probe.err"
  else
    if ! python3 - <<'PY'
import json
p='/tmp/watchdog_probe.json'
try:
    d=json.load(open(p,'r',encoding='utf-8'))
    ok=bool(d.get('ok'))
    raise SystemExit(0 if ok else 1)
except Exception:
    raise SystemExit(1)
PY
    then
      issues=$((issues+1))
      log_alert "gateway probe ok=false. restart may be required -> approval needed"
    fi
  fi

  # 5) inbound cleanup timer should stay active
  if ! systemctl --user is-active --quiet openclaw-inbound-cleanup.timer; then
    if systemctl --user start openclaw-inbound-cleanup.timer >/dev/null 2>&1; then
      log_state "softfix: started openclaw-inbound-cleanup.timer"
    else
      issues=$((issues+1))
      log_alert "cleanup timer inactive and failed to start"
    fi
  fi

  # 6) disk pressure
  local used
  used=$(df -P /home/openclawuser | awk 'NR==2{gsub(/%/,"",$5); print $5}')
  if [[ -n "$used" && "$used" -ge 90 ]]; then
    issues=$((issues+1))
    log_alert "disk usage high: ${used}%"
  fi

  # 7) recent critical errors in userbot logs (signal only)
  local err_count
  err_count=$(journalctl --user -u userbot.service --since "10 min ago" --no-pager 2>/dev/null | grep -Eic "Traceback|Unhandled error|TypeNotFoundError|Cannot get difference" || true)
  if [[ "$err_count" -ge 20 ]]; then
    log_alert "userbot high error rate in last 10m: count=${err_count} (no restart applied)"
  fi

  if [[ "$issues" -eq 0 ]]; then
    log_state "ok: all checks passed"
  else
    log_state "issues_detected=${issues}"
  fi
}

log_state "watchdog started: interval=${INTERVAL_SEC}s"
while true; do
  check_once
  sleep "$INTERVAL_SEC"
done

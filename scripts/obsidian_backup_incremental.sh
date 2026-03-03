#!/usr/bin/env bash
set -euo pipefail

SESSION_DIR="$HOME/.openclaw/agents/main/sessions"
VAULT_DIR="$HOME/.openclaw/workspace/Obsidian-Telegram-KB/50_ChatBackups"
STATE_DIR="$HOME/.openclaw/workspace/tmp/obsidian-backup"
LAST_FILE="$STATE_DIR/last_line_count"

mkdir -p "$VAULT_DIR" "$STATE_DIR"

LATEST="$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1 || true)"
[[ -z "$LATEST" || ! -f "$LATEST" ]] && exit 0

TOTAL_LINES=$(wc -l < "$LATEST")
LAST_LINES=$(cat "$LAST_FILE" 2>/dev/null || echo 0)
NEW_LINES=$((TOTAL_LINES - LAST_LINES))

# avoid noisy tiny snapshots
if (( NEW_LINES < 8 )); then
  exit 0
fi

START=$((LAST_LINES + 1))
TS=$(date +"%Y-%m-%d-%H%M")
OUT="$VAULT_DIR/${TS}-incremental.md"

{
  echo "# Chat Backup Incremental — $TS"
  echo
  echo "- Session: $(basename "$LATEST")"
  echo "- Lines: $START..$TOTAL_LINES"
  echo "- Saved: $(date -u +"%Y-%m-%d %H:%M UTC")"
  echo
  echo "---"
  echo

  tail -n +"$START" "$LATEST" | jq -r '
    select(.type=="message")
    | .message as $m
    | ($m.role // "unknown") as $r
    | (
        if ($m.content|type)=="string" then $m.content
        elif ($m.content|type)=="array" then
          ($m.content[]? | if .type=="text" then .text else empty end) | tostring
        else "" end
      ) as $txt
    | select(($txt|length) > 0)
    | "## [" + $r + "]\n\n" + ($txt | gsub("\r";"") ) + "\n"
  '
} > "$OUT"

echo "$TOTAL_LINES" > "$LAST_FILE"

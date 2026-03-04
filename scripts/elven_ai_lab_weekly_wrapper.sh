#!/usr/bin/env bash
set -euo pipefail
source /home/openclawuser/userbot/.venv/bin/activate
systemctl --user stop userbot || true
sleep 1
python /home/openclawuser/.openclaw/workspace/scripts/elven_ai_lab_poster.py weekly || true
systemctl --user start userbot || true

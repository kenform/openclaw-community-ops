#!/usr/bin/env bash
set -euo pipefail
python3 /home/openclawuser/.openclaw/workspace/scripts/elven_ai_lab_poster_bot.py slot >> /home/openclawuser/.openclaw/workspace/tmp/elven_ai_lab.log 2>&1 || true

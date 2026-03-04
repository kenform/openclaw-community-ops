#!/usr/bin/env bash
set -euo pipefail
/home/openclawuser/userbot/.venv/bin/python /home/openclawuser/.openclaw/workspace/scripts/autolearn_worker.py >> /home/openclawuser/.openclaw/workspace/tmp/autolearn.log 2>&1 || true

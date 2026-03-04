#!/usr/bin/env python3
import json, sys
from pathlib import Path

state = Path('/home/openclawuser/userbot/autolearn_state.json')
mode = (sys.argv[1] if len(sys.argv) > 1 else '').strip().lower()
if mode not in {'on','off'}:
    raise SystemExit('usage: autolearn_toggle.py on|off')

d = {}
if state.exists():
    try:
        d = json.loads(state.read_text(encoding='utf-8'))
    except Exception:
        d = {}

d['enabled'] = (mode == 'on')
state.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'autolearn={mode}')

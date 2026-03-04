#!/usr/bin/env python3
import datetime as dt
import json
import os
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

WORKSPACE = Path('/home/openclawuser/.openclaw/workspace')
VAULT = WORKSPACE / 'Obsidian-Telegram-KB'
CFG = WORKSPACE / 'scripts' / 'elven_ai_lab_config.json'
ENV = WORKSPACE / 'scripts' / 'elven_ai_lab_bot.env'
HISTORY = WORKSPACE / 'tmp' / 'elven_ai_lab_history.json'


def load_env(path: Path):
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k,v = line.split('=',1)
            out[k.strip()] = v.strip()
    return out


def load_cfg():
    if CFG.exists():
        return json.loads(CFG.read_text(encoding='utf-8'))
    return {"enabled": True}


def load_history():
    if HISTORY.exists():
        try:
            return json.loads(HISTORY.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {"posts": []}


def save_history(h):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding='utf-8')


def prune_history(h, hours=48):
    now = dt.datetime.now(dt.timezone.utc)
    keep = []
    for x in h.get('posts', []):
        try:
            ts = dt.datetime.fromisoformat(x['ts'].replace('Z', '+00:00'))
        except Exception:
            continue
        if (now - ts).total_seconds() <= hours * 3600:
            keep.append(x)
    h['posts'] = keep
    return h


def collect_notes(limit=40):
    roots = [VAULT / '10_Channels', VAULT / '20_Summaries', VAULT / 'Crypto']
    files = []
    for r in roots:
        if r.exists():
            files.extend(r.rglob('*.md'))
    files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

    out = []
    for f in files:
        txt = f.read_text(encoding='utf-8', errors='ignore')
        low = txt.lower()
        score = 0
        for kw in ['openclaw','agent','automation','telegram','obsidian','ai','workflow','research','security','polymarket']:
            if kw in low:
                score += 1
        if 'relevance: high' in low:
            score += 3
        if score < 2:
            continue

        title = f.stem
        for line in txt.splitlines():
            if line.startswith('# '):
                title = line[2:].strip(); break

        bullets = []
        for line in txt.splitlines():
            l = line.strip()
            if l.startswith('- ') and len(l) > 8:
                bullets.append(l[2:].strip())
            if len(bullets) >= 3:
                break
        if not bullets:
            for line in txt.splitlines():
                l = line.strip()
                if len(l) > 40 and not l.startswith('#') and not l.startswith('---'):
                    bullets.append(l[:180])
                if len(bullets) >= 2:
                    break

        out.append({"title": title, "bullets": bullets[:3], "score": score})
        if len(out) >= limit:
            break
    return out


def build_post(slot_idx: int):
    notes = collect_notes(50)
    h = prune_history(load_history(), 48)
    used = set((x.get('title','').strip().lower()) for x in h.get('posts', []))
    pool = [n for n in notes if n['title'].strip().lower() not in used] or notes
    if not pool:
        return None

    n = pool[0]
    ptype_seq = ['signal','tool','guide','business','research','ops']
    ptype = ptype_seq[len(h.get('posts', [])) % len(ptype_seq)]
    head = {
        'signal': ('⚡ AI Signal', 'Короткий сигнал:'),
        'tool': ('🧰 Tool Breakdown', 'Разбор инструмента:'),
        'guide': ('🤖 Automation Guide', 'Практический сценарий:'),
        'business': ('📈 AI Business', 'Бизнес-угол:'),
        'research': ('🔍 Research Note', 'Ресерч-выжимка:'),
        'ops': ('🧪 Operational Tip', 'Операционный совет:'),
    }[ptype]

    bullets = '\n'.join([f"• {b}" for b in (n['bullets'] or ['Требуется ручная проверка источника.'])])
    msg = f"{head[0]}\n\n{head[1]} {n['title']}\n{bullets}\n\nПочему важно:\n• Помогает быстрее принимать решения без инфошума."

    h.setdefault('posts', []).append({
        'ts': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z'),
        'title': n['title'],
        'type': ptype
    })
    save_history(h)
    return msg


def send_telegram(token: str, channel: str, text: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urlencode({
        'chat_id': channel,
        'text': text,
        'disable_web_page_preview': 'true'
    }).encode('utf-8')
    req = Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urlopen(req, timeout=20) as r:
        body = r.read().decode('utf-8', errors='ignore')
    return body


def main(mode='slot'):
    cfg = load_cfg()
    if not cfg.get('enabled', True):
        return
    env = load_env(ENV)
    token = env['BOT_TOKEN']
    channel = env['CHANNEL']

    if mode == 'weekly':
        notes = collect_notes(20)
        top = '\n'.join([f"• {x['title']}" for x in notes[:10]]) if notes else '• Нет новых сильных сигналов'
        msg = f"🗓 Weekly Digest — Top 10\n\n{top}\n\nПочему важно:\n• Это концентрат сильных сигналов за неделю."
    else:
        slot_idx = dt.datetime.utcnow().hour % 6
        msg = build_post(slot_idx)

    if not msg:
        return

    lines = [l for l in msg.splitlines() if l.strip()]
    if not (8 <= len(lines) <= 14):
        return

    send_telegram(token, channel, msg)


if __name__ == '__main__':
    import sys
    m = sys.argv[1] if len(sys.argv) > 1 else 'slot'
    main(m)

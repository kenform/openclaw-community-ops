#!/usr/bin/env python3
import asyncio
import datetime as dt
import json
import random
from pathlib import Path
from telethon import TelegramClient

WORKSPACE = Path('/home/openclawuser/.openclaw/workspace')
CFG = WORKSPACE / 'scripts' / 'elven_ai_lab_config.json'
USERBOT_ENV = Path('/home/openclawuser/userbot/config.env')
SESSION = '/home/openclawuser/userbot/session.session'
VAULT = WORKSPACE / 'Obsidian-Telegram-KB'
HISTORY_PATH = WORKSPACE / 'tmp' / 'elven_ai_lab_history.json'


def load_cfg():
    if not CFG.exists():
        return {
            'channel_name': 'Elven AI Lab',
            'language': 'ru',
            'max_lines': 12,
            'min_lines': 8,
            'daily_slots': ['09:00','12:00','15:00','18:00','21:00','23:00'],
            'enabled': True
        }
    return json.loads(CFG.read_text(encoding='utf-8'))


def load_env(path: Path):
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k,v = line.split('=',1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out




def load_history():
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding='utf-8'))
        except Exception:
            return {'posts': []}
    return {'posts': []}


def save_history(h):
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding='utf-8')


def prune_history(h, hours=48):
    now = dt.datetime.now(dt.timezone.utc)
    kept=[]
    for x in h.get('posts',[]):
        try:
            ts=dt.datetime.fromisoformat(x['ts'].replace('Z','+00:00'))
        except Exception:
            continue
        if (now-ts).total_seconds() <= hours*3600:
            kept.append(x)
    h['posts']=kept
    return h


def recently_used_titles(h):
    return set((x.get('title') or '').strip().lower() for x in h.get('posts',[]))


def next_post_type(h):
    seq=['signal','tool','guide','business','research','ops']
    n=len(h.get('posts',[]))
    return seq[n % len(seq)]


def collect_high_relevance_notes(limit=40):
    roots = [
        VAULT / '10_Channels',
        VAULT / '20_Summaries',
        VAULT / 'Crypto',
    ]
    files = []
    for r in roots:
        if r.exists():
            files.extend(r.rglob('*.md'))
    files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

    out = []
    for f in files:
        try:
            txt = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
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

        # extract 2 short signal lines
        bullets = []
        for line in txt.splitlines():
            l=line.strip()
            if l.startswith('- ') and len(l) > 6:
                bullets.append(l[2:].strip())
            if len(bullets) >= 3:
                break
        if not bullets:
            # fallback: first non-empty sentence-like lines
            for line in txt.splitlines():
                l=line.strip()
                if len(l) > 30 and not l.startswith('#') and not l.startswith('---'):
                    bullets.append(l[:180])
                if len(bullets) >= 2:
                    break

        out.append({'path': str(f), 'title': title, 'bullets': bullets[:3], 'score': score})
        if len(out) >= limit:
            break
    return out


def latest_insights(limit=20):
    files = sorted((VAULT / '20_Summaries').glob('*.md'), key=lambda p: p.stat().st_mtime, reverse=True)
    snippets = []
    for p in files[:limit]:
        txt = p.read_text(encoding='utf-8', errors='ignore')
        title = txt.splitlines()[0].replace('#','').strip() if txt else p.stem
        snippets.append((p, title))
    return snippets


def pick_post(slot_idx: int):
    notes = collect_high_relevance_notes(50)
    h = prune_history(load_history(), hours=48)
    used = recently_used_titles(h)

    # filter out recent titles
    fresh = [n for n in notes if (n.get('title','').strip().lower() not in used)]
    pool = fresh if fresh else notes
    if not pool:
        return "⚪️ NO POST\n\nНет достаточно ценных материалов для публикации в этом цикле.", None

    n = pool[0]
    title = n['title']
    b = n['bullets'] if n['bullets'] else ["Сигналы не извлечены автоматически, требуется ручная проверка."]

    ptype = next_post_type(h)
    templates = {
        'signal': ("⚡ AI Signal", "Короткий сигнал по теме дня:"),
        'tool': ("🧰 Tool Breakdown", "Разбор инструмента/подхода:"),
        'guide': ("🤖 Automation Guide", "Практический сценарий автоматизации:"),
        'business': ("📈 AI Business", "Бизнес-угол и применение:"),
        'research': ("🔍 Research Note", "Ресерч-выжимка:"),
        'ops': ("🧪 Operational Tip", "Операционный совет на сегодня:"),
    }
    h1, lead = templates.get(ptype, templates['signal'])

    pts = "\n".join([f"• {x}" for x in b[:3]])
    msg = f"{h1}\n\n{lead} {title}\n{pts}\n\nПочему важно:\n• Помогает принимать решения быстрее и с меньшим шумом."

    # save history marker
    h.setdefault('posts', []).append({'ts': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z'), 'title': title, 'type': ptype})
    save_history(h)
    return msg, ptype


def build_weekly_digest():
    insights = latest_insights(50)
    top = [t for _, t in insights[:10]]
    bullets = '\n'.join([f"• {x}" for x in top]) if top else '• Нет новых релевантных материалов'
    return f"""🗓 Weekly Digest — Top 10 AI/Automation Signals

{bullets}

Почему важно:
Эти темы формируют практический стек: AI агенты, automation, инфраструктура и монетизация."""


async def publish(mode='slot'):
    cfg = load_cfg()
    if not cfg.get('enabled', True):
        return

    env = load_env(USERBOT_ENV)
    client = TelegramClient(SESSION, int(env['TELEGRAM_API_ID']), env['TELEGRAM_API_HASH'])
    await client.start()

    target = None
    dialogs = await client.get_dialogs(limit=400)
    for d in dialogs:
        if (d.name or '').strip().lower() == cfg['channel_name'].strip().lower():
            target = d.entity
            break
    if not target:
        for d in dialogs:
            if cfg['channel_name'].strip().lower() in (d.name or '').lower():
                target = d.entity
                break

    if not target:
        await client.disconnect()
        return

    if mode == 'weekly':
        msg = build_weekly_digest()
    else:
        now = dt.datetime.utcnow()
        slot_idx = now.hour % 6
        msg, _ptype = pick_post(slot_idx)

    # Quality filter: basic line count guard
    lines = [x for x in msg.splitlines() if x.strip()]
    if not (8 <= len(lines) <= 14):
        await client.disconnect()
        return

    await client.send_message(target, msg, link_preview=False)
    await client.disconnect()


if __name__ == '__main__':
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else 'slot'
    asyncio.run(publish(mode))

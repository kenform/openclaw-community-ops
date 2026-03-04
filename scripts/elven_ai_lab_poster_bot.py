#!/usr/bin/env python3
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

WORKSPACE = Path('/home/openclawuser/.openclaw/workspace')
VAULT = WORKSPACE / 'Obsidian-Telegram-KB'
CFG = WORKSPACE / 'scripts' / 'elven_ai_lab_config.json'
ENV = WORKSPACE / 'scripts' / 'elven_ai_lab_bot.env'
HISTORY = WORKSPACE / 'tmp' / 'elven_ai_lab_history.json'

MAX_POSTS_PER_DAY = 6
MAX_LINES = 12


def load_env(path: Path):
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1)
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


def prune_history(h, hours=168):
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


def today_post_count(h):
    today = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
    c = 0
    for x in h.get('posts', []):
        if str(x.get('ts', '')).startswith(today):
            c += 1
    return c


def first_match(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ''


def collect_notes(limit=60):
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

        # low-value skip
        bad = ['мем', 'реферал', 'купи', 'подпишись', 'розыгрыш', 'giveaway', 'ad', 'реклама']
        if any(x in low for x in bad):
            continue

        # useful priority scoring
        score = 0
        good = [
            'openclaw', 'automation', 'telegram', 'agent', 'ai', 'guide', 'гайд',
            'пошаг', 'команда', 'config', 'ошибка', 'fix', 'решение', 'инсайт', 'product', 'update'
        ]
        for kw in good:
            if kw in low:
                score += 1
        if 'relevance: high' in low:
            score += 3
        if score < 2:
            continue

        title = f.stem
        for line in txt.splitlines():
            if line.startswith('# '):
                title = line[2:].strip()
                break

        bullets = []
        for line in txt.splitlines():
            l = line.strip()
            if l.startswith('- ') and len(l) > 15:
                bullets.append(re.sub(r'\s+', ' ', l[2:]).strip()[:120])
            if len(bullets) >= 3:
                break
        if not bullets:
            for line in txt.splitlines():
                l = line.strip()
                if len(l) > 45 and not l.startswith('#') and not l.startswith('---'):
                    bullets.append(re.sub(r'\s+', ' ', l)[:120])
                if len(bullets) >= 3:
                    break

        source_name = first_match(r'^Source:\s*(.+)$', txt)
        source_url = first_match(r'^URL:\s*(https?://\S+)$', txt)

        out.append({
            'title': title[:90],
            'bullets': bullets[:3],
            'score': score,
            'source_name': source_name or 'unknown',
            'source_url': source_url,
        })
        if len(out) >= limit:
            break
    return out


def sanitize_channel_name(name: str):
    n = (name or '').strip()
    n = n.replace('https://t.me/', '').replace('@', '').strip('/')
    return n or 'unknown'


def render_post(n, channel_link, chat_link):
    title = n['title']
    bullets = n['bullets'] or ['Короткий технический сигнал без лишнего шума.']
    source_name = sanitize_channel_name(n.get('source_name') or 'unknown')
    source_url = n.get('source_url') or channel_link

    lines = [
        f"{title}",
        "Ключевое по теме:",
        f"• {bullets[0]}",
    ]
    if len(bullets) > 1:
        lines.append(f"• {bullets[1]}")
    if len(bullets) > 2:
        lines.append(f"• {bullets[2]}")

    lines += [
        "Why it matters: помогает принимать решения быстрее и точнее.",
        f"Source: @{source_name}",
        "———",
        "🌿 ARIA • Elven AI",
        "#ai #openclaw #automation #telegram",
        f"[Source]({source_url}) | [Channel]({channel_link}) | [Chat]({chat_link})",
    ]

    # hard line cap
    non_empty = [x for x in lines if x.strip()]
    return '\n'.join(non_empty[:MAX_LINES])


def build_post():
    h = prune_history(load_history(), 168)
    if today_post_count(h) >= MAX_POSTS_PER_DAY:
        return None

    notes = collect_notes(80)
    used_titles = set((x.get('title', '').strip().lower()) for x in h.get('posts', []))
    pool = [n for n in notes if n['title'].strip().lower() not in used_titles] or notes
    if not pool:
        return None

    env = load_env(ENV)
    channel_link = env.get('CHANNEL_LINK', 'https://t.me/Elven_Ai_Lab')
    chat_link = env.get('CHAT_LINK', channel_link)

    n = sorted(pool, key=lambda x: x.get('score', 0), reverse=True)[0]
    msg = render_post(n, channel_link, chat_link)

    h.setdefault('posts', []).append({
        'ts': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'title': n['title'],
        'score': n.get('score', 0),
        'source': n.get('source_name', ''),
    })
    save_history(h)
    return msg


def send_telegram(token: str, channel: str, text: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urlencode({
        'chat_id': channel,
        'text': text,
        'disable_web_page_preview': 'true',
        'parse_mode': 'Markdown'
    }).encode('utf-8')
    req = Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8', errors='ignore')


def main(mode='slot'):
    cfg = load_cfg()
    if not cfg.get('enabled', True):
        return

    env = load_env(ENV)
    token = env['BOT_TOKEN']
    channel = env['CHANNEL']

    msg = build_post()
    if not msg:
        return

    # strict line guard
    lines = [l for l in msg.splitlines() if l.strip()]
    if len(lines) > MAX_LINES:
        msg = '\n'.join(lines[:MAX_LINES])

    send_telegram(token, channel, msg)


if __name__ == '__main__':
    import sys
    m = sys.argv[1] if len(sys.argv) > 1 else 'slot'
    main(m)

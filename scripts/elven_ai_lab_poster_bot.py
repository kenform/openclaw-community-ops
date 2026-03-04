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

MAX_SIGNALS_PER_DAY = 20
POST_TYPES = ["AI SIGNAL", "TOOL", "HOW TO", "TREND", "WEEKLY DIGEST"]


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


def today_count_by_layer(h, layer: str):
    today = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
    return sum(1 for x in h.get('posts', []) if str(x.get('ts', '')).startswith(today) and x.get('layer') == layer)


def first_match(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ''


def sanitize_channel_name(name: str):
    n = (name or '').strip()
    n = n.replace('https://t.me/', '').replace('@', '').strip('/')
    return n or 'unknown'


def score_text(low: str):
    bad = ['мем', 'реферал', 'купи', 'подпишись', 'розыгрыш', 'giveaway', 'ad', 'реклама', 'мотивац', 'вдохнов']
    if any(x in low for x in bad):
        return 0
    score = 25
    good = [
        'openclaw', 'automation', 'telegram', 'agent', 'ai', 'guide', 'гайд',
        'пошаг', 'команда', 'config', 'ошибка', 'fix', 'решение', 'инсайт',
        'product', 'update', 'tool', 'workflow', 'api', 'архитект'
    ]
    for kw in good:
        if kw in low:
            score += 6
    return min(100, score)


def collect_notes(limit=120):
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
        score = score_text(low)
        if score < 60:
            continue

        title = f.stem
        for line in txt.splitlines():
            if line.startswith('# '):
                title = line[2:].strip()
                break

        bullets = []
        for line in txt.splitlines():
            l = line.strip()
            if l.startswith('- ') and len(l) > 20:
                bullets.append(re.sub(r'\s+', ' ', l[2:]).strip())
            if len(bullets) >= 3:
                break
        if not bullets:
            for line in txt.splitlines():
                l = line.strip()
                if len(l) > 50 and not l.startswith('#') and not l.startswith('---'):
                    bullets.append(re.sub(r'\s+', ' ', l).strip())
                if len(bullets) >= 3:
                    break

        source_name = first_match(r'^Source:\s*(.+)$', txt)
        source_url = first_match(r'^URL:\s*(https?://\S+)$', txt)

        out.append({
            'title': title[:100],
            'bullets': bullets[:3],
            'score': score,
            'source_name': source_name or 'unknown',
            'source_url': source_url,
        })
        if len(out) >= limit:
            break
    return out


def signal_level(score: int):
    if score >= 80:
        return '🜂 HIGH SIGNAL'
    if score >= 60:
        return '🜁 MEDIUM SIGNAL'
    return '🜃 LOW SIGNAL'


def render_post(n, channel_link, chat_link, post_type='AI SIGNAL'):
    title = n['title']
    bullets = n['bullets'] or ['Короткий технический сигнал без лишнего шума.']
    source_name = sanitize_channel_name(n.get('source_name') or 'unknown')
    source_url = n.get('source_url') or channel_link

    out = [
        signal_level(n.get('score', 0)),
        f"◆ ARIA • {post_type}",
        title,
        'Контекст:',
    ]

    for b in bullets[:3]:
        short = b[:95]
        extra = b[95:260].strip()
        out.append(f"• {short}")
        if extra:
            out.append(f"«||{extra}||»")

    out += [
        'Why it matters: помогает принимать решения без инфошума.',
        f'Source: @{source_name}',
        '───',
        '🌿 ARIA • Elven AI',
        '#ai #openclaw #automation #agents',
        f'[Source]({source_url}) | [Channel]({channel_link}) | [Chat]({chat_link})',
    ]
    return '\n'.join([x for x in out if x.strip()])


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


def main():
    cfg = load_cfg()
    if not cfg.get('enabled', True):
        return

    env = load_env(ENV)
    token = env['BOT_TOKEN']

    # layers
    signals_channel = env.get('SIGNALS_CHANNEL', env.get('CHANNEL', '@Elven_Ai_Lab'))
    raw_channel = env.get('RAW_CHANNEL', '')
    research_channel = env.get('RESEARCH_CHANNEL', '')

    channel_link = env.get('CHANNEL_LINK', 'https://t.me/Elven_Ai_Lab')
    chat_link = env.get('CHAT_LINK', channel_link)

    h = prune_history(load_history(), 168)
    notes = collect_notes(120)
    if not notes:
        return

    used_titles = set((x.get('title', '').strip().lower()) for x in h.get('posts', []))
    pool = [n for n in notes if n['title'].strip().lower() not in used_titles] or notes
    n = sorted(pool, key=lambda x: x.get('score', 0), reverse=True)[0]

    score = int(n.get('score', 0))
    ptype = POST_TYPES[(today_count_by_layer(h, 'signals') + today_count_by_layer(h, 'raw')) % len(POST_TYPES)]
    msg = render_post(n, channel_link, chat_link, ptype)

    # routing by score
    if score < 60:
        return
    elif 60 <= score < 80:
        if raw_channel:
            send_telegram(token, raw_channel, msg)
            layer = 'raw'
        else:
            return
    else:
        if today_count_by_layer(h, 'signals') >= MAX_SIGNALS_PER_DAY:
            return
        send_telegram(token, signals_channel, msg)
        layer = 'signals'

    h.setdefault('posts', []).append({
        'ts': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'title': n['title'],
        'score': score,
        'source': n.get('source_name', ''),
        'layer': layer,
        'type': ptype,
    })
    save_history(h)


if __name__ == '__main__':
    main()

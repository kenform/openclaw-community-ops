#!/usr/bin/env python3
import datetime as dt
import hashlib
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

MAX_SIGNALS_PER_DAY = 24
POST_TYPES = ["AI SIGNAL", "TOOL", "HOW TO", "TREND", "WEEKLY DIGEST"]
SIGNALS_MIN_SCORE = 60
RAW_MIN_SCORE = 45


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
    m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else ''


def sanitize_channel_name(name: str):
    n = (name or '').strip()
    n = n.replace('https://t.me/', '').replace('@', '').strip('/')
    return n


def score_text(low: str):
    bad_patterns = [
        r'\bмем\w*\b', r'\bреферал\w*\b', r'\bкупи\w*\b', r'\bподпиш\w*\b',
        r'\bрозыгрыш\w*\b', r'\bgiveaway\b', r'\bреклама\w*\b', r'\bмотивац\w*\b', r'\bвдохнов\w*\b'
    ]
    if any(re.search(p, low, re.IGNORECASE) for p in bad_patterns):
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


def ambiguity_reason(low: str) -> str:
    reasons = []
    if any(k in low for k in ['кажется', 'возможно', 'слух', 'rumor', 'мнение', 'opinion']):
        reasons.append('много предположений, мало проверяемых фактов')
    if not any(k in low for k in ['цифр', 'data', 'метрик', 'официаль', 'source:', 'url:']):
        reasons.append('нет явных метрик/источников в тексте')
    return '; '.join(reasons[:1])


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
        if score < RAW_MIN_SCORE:
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
            'bullets': bullets[:6],
            'score': score,
            'source_name': sanitize_channel_name(source_name),
            'source_url': source_url,
            'unclear': ambiguity_reason(low),
        })
        if len(out) >= limit:
            break
    return out


def pick_context_tags(text: str):
    low = (text or '').lower()
    tags = []
    if any(k in low for k in ['ai', 'agent', 'ии', 'агент']):
        tags.append('#ai')
    if any(k in low for k in ['automation', 'автомат', 'workflow']):
        tags.append('#automation')
    if any(k in low for k in ['telegram', 'канал', 'тг']):
        tags.append('#telegram')
    if any(k in low for k in ['tool', 'sdk', 'api', 'инструмент']):
        tags.append('#tools')
    if any(k in low for k in ['guide', 'гайд', 'how to', 'пошаг']):
        tags.append('#guide')
    if any(k in low for k in ['crypto', 'solana', 'ethereum', 'btc', 'defi']):
        tags.append('#crypto')
    for d in ['#ai', '#automation', '#agents', '#telegram']:
        if len(tags) >= 3:
            break
        if d not in tags:
            tags.append(d)
    return ' '.join(tags[:5])

def signal_level(score: int):
    if score >= 80:
        return '🜂 HIGH SIGNAL'
    if score >= 60:
        return '🜁 MEDIUM SIGNAL'
    return '🜃 LOW SIGNAL'


def note_signature(n: dict) -> str:
    base = (n.get('title', '').strip().lower() + '|' + ' '.join((n.get('bullets') or [])[:2]).strip().lower())
    return hashlib.sha1(base.encode('utf-8', errors='ignore')).hexdigest()


def is_buggy_unknown_note(n: dict) -> bool:
    source_name = (n.get('source_name') or '').strip().lower()
    title = (n.get('title') or '').strip().lower()
    # Block known bad pattern: unknown source + repeating polymarket checklist
    if not source_name and ('полимаркет — следующие шаги' in title or 'polymarket' in title):
        return True
    return False


def render_post(n, channel_link, chat_link, exchange_link, post_type='AI SIGNAL'):
    title = n['title']
    bullets = n['bullets'] or ['Короткий технический сигнал без лишнего шума.']
    source_name = sanitize_channel_name(n.get('source_name') or '')
    source_url = n.get('source_url') or channel_link

    source_line = f'<a href="{source_url}">{source_name}</a>' if source_name else f'<a href="{source_url}">Источник</a>'

    out = [
        f"✨ {post_type.title()}",
        source_line,
        title,
        "",
        "Главное:",
    ]

    for b in bullets[:3]:
        short = b[:125]
        extra = b[125:300].strip()
        out.append(f"• {short}")
        if extra:
            out.append(f"<a href=\"{source_url}\">Читать подробнее</a>")
            out.append(f"<blockquote expandable>{extra}</blockquote>")

    out += [
        "",
        "🌿 Elven AI Lab",
        "",
        "Ссылки:",
        f'<a href="{exchange_link}">Биржи</a> | <a href="{channel_link}">Канал</a> | <a href="{chat_link}">Чат</a>',
        pick_context_tags(' '.join(bullets) + ' ' + title),
    ]
    return '\n'.join([x for x in out if x is not None])


def send_telegram(token: str, channel: str, text: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urlencode({
        'chat_id': channel,
        'text': text,
        'disable_web_page_preview': 'true',
        'parse_mode': 'HTML'
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
    exchange_link = env.get('EXCHANGE_LINK', 'https://eragon-exchange-site-next-kenformgod-6184s-projects.vercel.app/')

    h = prune_history(load_history(), 168)
    notes = collect_notes(120)
    if not notes:
        return

    used_titles = set((x.get('title', '').strip().lower()) for x in h.get('posts', []))
    used_sigs = set((x.get('sig', '') for x in h.get('posts', [])))

    clean_notes = [n for n in notes if not is_buggy_unknown_note(n)]
    if not clean_notes:
        return

    pool = [
        n for n in clean_notes
        if n['title'].strip().lower() not in used_titles and note_signature(n) not in used_sigs
    ]

    # strict no-repost mode: if nothing new, skip publish
    if not pool:
        return

    # avoid immediate repeat of last signature
    if h.get('posts'):
        last_sig = h['posts'][-1].get('sig', '')
        pool2 = [n for n in pool if note_signature(n) != last_sig]
        if not pool2:
            return
        pool = pool2

    n = sorted(pool, key=lambda x: x.get('score', 0), reverse=True)[0]

    score = int(n.get('score', 0))
    ptype = POST_TYPES[(today_count_by_layer(h, 'signals') + today_count_by_layer(h, 'raw')) % len(POST_TYPES)]
    msg = render_post(n, channel_link, chat_link, exchange_link, ptype)

    # routing by score
    if score < RAW_MIN_SCORE:
        return
    elif RAW_MIN_SCORE <= score < SIGNALS_MIN_SCORE:
        target = raw_channel or signals_channel
        send_telegram(token, target, msg)
        layer = 'raw' if raw_channel else 'signals'
    else:
        if today_count_by_layer(h, 'signals') >= MAX_SIGNALS_PER_DAY:
            return
        send_telegram(token, signals_channel, msg)
        layer = 'signals'

    h.setdefault('posts', []).append({
        'ts': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'title': n['title'],
        'sig': note_signature(n),
        'score': score,
        'source': n.get('source_name', ''),
        'source_url': n.get('source_url', ''),
        'layer': layer,
        'type': ptype,
    })
    save_history(h)


if __name__ == '__main__':
    main()

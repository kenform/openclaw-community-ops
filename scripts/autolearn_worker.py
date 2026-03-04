#!/usr/bin/env python3
import asyncio
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path
from telethon import TelegramClient

BASE = Path('/home/openclawuser/userbot')
VAULT = Path('/home/openclawuser/vault') / 'AutoLearning' / 'Telegram'
INDEX = Path('/home/openclawuser/vault/AutoLearning/telegram_ingest_index.json')
INBOX = BASE / 'autolearn_inbox.jsonl'
STATE = BASE / 'autolearn_state.json'
LAST_DIGEST = BASE / 'autolearn_last_digest.md'
MAX_PER_NIGHT = 120
TZ_OFFSET = 3  # MSK UTC+3


def load_env():
    e = {}
    for ln in (BASE / 'config.env').read_text(encoding='utf-8').splitlines():
        if '=' in ln and not ln.strip().startswith('#'):
            k, v = ln.split('=', 1)
            e[k.strip()] = v.strip()
    return e


def now_msk():
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) + dt.timedelta(hours=TZ_OFFSET)


def in_window():
    h = now_msk().hour
    return 0 <= h < 8


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {
        'enabled': True,
        'last_run': None,
        'last_digest_day': '',
        'today': {'day': now_msk().strftime('%Y-%m-%d'), 'received': 0, 'saved': 0, 'processed': 0, 'top': []}
    }


def save_state(s):
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding='utf-8')


def load_index():
    if INDEX.exists():
        try:
            return json.loads(INDEX.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'items': {}}


def save_index(x):
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')


def normalize_text(t: str) -> str:
    t = re.sub(r'http\S+', ' ', (t or '').lower())
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def hash_post(text: str, url: str) -> str:
    src = normalize_text(text) + '|' + (url or '').strip().lower()
    return hashlib.sha1(src.encode('utf-8')).hexdigest()


def score_post(text: str) -> int:
    t = (text or '').lower()
    if len(t) < 120:
        return 20
    s = 35
    plus = [
        'как', 'пошаг', 'инструкц', 'гайд', 'команд', 'config', 'настрой',
        'ошибк', 'fix', 'почин', 'метрик', 'цифр', 'рост', 'стратег', 'монет', 'продукт'
    ]
    minus = ['мем', 'реферал', 'купи', 'розыгрыш', 'подпишись', 'реклама']
    s += sum(8 for k in plus if k in t)
    s -= sum(12 for k in minus if k in t)
    return max(0, min(100, s))


def extract_title(text: str, source: str) -> str:
    line = (text or '').strip().split('\n')[0][:90].strip()
    line = re.sub(r'[#*`_\[\]]', '', line)
    if len(line) < 8:
        line = f'{source} update'
    return line


def summarize(text: str):
    clean = re.sub(r'\s+', ' ', text or '').strip()
    summary = clean[:260]
    parts = re.split(r'(?<=[.!?])\s+', clean)
    bullets = []
    for p in parts:
        p = p.strip('-• ').strip()
        if len(p) > 25:
            bullets.append(p[:160])
        if len(bullets) >= 5:
            break
    if not bullets and clean:
        bullets = [clean[:150]]
    return summary, bullets


def make_tags(text: str):
    t = (text or '').lower()
    tags = ['#telegram', '#automation']
    if 'ai' in t:
        tags.append('#ai')
    if 'openclaw' in t:
        tags.append('#openclaw')
    if any(x in t for x in ['бот', 'bot']):
        tags.append('#bots')
    if any(x in t for x in ['крипт', 'defi', 'bitcoin']):
        tags.append('#crypto')
    return sorted(set(tags))[:7]


def note_path(source: str, title: str, date_iso: str):
    d = dt.datetime.fromisoformat(date_iso.replace('Z', '+00:00')) if 'T' in date_iso else dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    ym = d.strftime('%Y-%m')
    day = d.strftime('%Y-%m-%d')
    src = re.sub(r'[^a-zA-Z0-9а-яА-Я_-]+', '-', (source or 'source'))[:24]
    st = re.sub(r'[^a-zA-Z0-9а-яА-Я_-]+', '-', title.lower())[:40]
    folder = VAULT / ym
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f'{day}__{src}__{st}.md'


def render_note(ev, score, title, summary, bullets, tags):
    source = ev.get('source', '-')
    url = ev.get('url') or ev.get('message_link') or '-'
    date = ev.get('date') or dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat() + 'Z'
    text = (
        f"# {title}\n\n"
        f"Source: {source}\n"
        f"URL: {url}\n"
        f"Date: {date}\n"
        f"Score: {score}/100\n\n"
        f"## Summary\n{summary}\n\n"
        f"## Key points\n" + '\n'.join([f"- {x}" for x in bullets[:7]]) + "\n\n"
        f"## Commands / Steps (если есть)\n```bash\n# n/a\n```\n\n"
        f"## Tags\n" + ' '.join(tags) + "\n\n"
        f"## Why it matters\nПомогает быстрее принимать решения и внедрять рабочие практики.\n"
    )
    return text


async def send_saved_message(text: str):
    e = load_env()
    c = TelegramClient(str(BASE / 'session'), int(e['TELEGRAM_API_ID']), e['TELEGRAM_API_HASH'])
    await c.start()
    await c.send_message('me', text)
    await c.disconnect()


def load_events():
    if not INBOX.exists():
        return []
    rows = []
    for ln in INBOX.read_text(encoding='utf-8', errors='ignore').splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except Exception:
            continue
    return rows


def save_remaining(rows):
    if not rows:
        INBOX.write_text('', encoding='utf-8')
        return
    INBOX.write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in rows) + '\n', encoding='utf-8')


def ensure_today(st):
    d = now_msk().strftime('%Y-%m-%d')
    if st.get('today', {}).get('day') != d:
        st['today'] = {'day': d, 'received': 0, 'saved': 0, 'processed': 0, 'top': []}


async def main():
    force = '--force' in os.sys.argv
    st = load_state()
    ensure_today(st)

    if not st.get('enabled', True):
        return
    if (not force) and (not in_window()):
        # 08:00 digest dispatch once
        m = now_msk()
        if m.hour >= 8 and st.get('last_digest_day') != st['today']['day']:
            top = sorted(st['today'].get('top', []), key=lambda x: x.get('score', 0), reverse=True)[:5]
            top_lines = '\n'.join([f"- {x['title']} | {x.get('url','-')}" for x in top]) if top else '- нет'
            digest = (
                f"📘 AutoLearning Daily Digest ({st['today']['day']})\n"
                f"Получено: {st['today'].get('received',0)}\n"
                f"Сохранено: {st['today'].get('saved',0)}\n\n"
                f"Top-5:\n{top_lines}\n\n"
                f"3 инсайта:\n"
                f"- Делай ставку на практические инструкции и кейсы\n"
                f"- Убирай шумные источники через .dl_mute\n"
                f"- Поддерживай лимиты для стабильного парсинга"
            )
            LAST_DIGEST.write_text(digest, encoding='utf-8')
            await send_saved_message(digest)
            st['last_digest_day'] = st['today']['day']
            save_state(st)
        return

    idx = load_index()
    items = idx.setdefault('items', {})
    rows = load_events()
    if not rows:
        st['last_run'] = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat() + 'Z'
        save_state(st)
        return

    keep = []
    processed_night = st['today'].get('processed', 0)

    for ev in rows:
        st['today']['received'] += 1
        if processed_night >= MAX_PER_NIGHT:
            keep.append(ev)
            continue

        text = ev.get('text', '') or ''
        url = ev.get('url') or ev.get('message_link') or ''
        h = hash_post(text, url)
        if h in items:
            continue

        sc = score_post(text)
        if sc < 65:
            continue

        title = extract_title(text, ev.get('source', 'source'))
        summary, bullets = summarize(text)
        tags = make_tags(text)
        body = render_note(ev, sc, title, summary, bullets, tags)
        path = note_path(ev.get('source', 'source'), title, ev.get('date') or dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat() + 'Z')
        path.write_text(body, encoding='utf-8')

        items[h] = {
            'ts': dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat() + 'Z',
            'source': ev.get('source', ''),
            'url': url,
            'score': sc,
            'path': str(path)
        }
        st['today']['saved'] += 1
        st['today']['processed'] += 1
        processed_night += 1
        st['today'].setdefault('top', []).append({'title': title, 'url': url, 'score': sc})
        st['today']['top'] = sorted(st['today']['top'], key=lambda x: x['score'], reverse=True)[:20]

        await asyncio.sleep(0.6)

    save_remaining(keep)
    save_index(idx)
    st['last_run'] = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat() + 'Z'
    save_state(st)


if __name__ == '__main__':
    asyncio.run(main())

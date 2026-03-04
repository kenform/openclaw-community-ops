#!/usr/bin/env python3
import os
import re
import json
import sqlite3
import hashlib
import datetime as dt
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

WORKSPACE = Path('/home/openclawuser/.openclaw/workspace')
VAULT = WORKSPACE / 'Obsidian-Telegram-KB'
CFG_PATH = WORKSPACE / 'scripts' / 'x_youtube_monitor_config.json'
STATE_DIR = WORKSPACE / 'tmp' / 'x_youtube_monitor'
DB_PATH = STATE_DIR / 'seen.db'

STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_cfg():
    if not CFG_PATH.exists():
        return {
            "x": {"handles": [], "rss_urls": [], "nitter_base": "https://nitter.net"},
            "youtube": {"channel_ids": [], "feed_urls": []},
            "relevance_keywords": ["openclaw", "polymarket", "ai", "agent", "crypto"],
            "high_relevance_min_hits": 2,
            "enable_youtube_transcript": False,
            "enable_whisper_fallback": False,
        }
    return json.loads(CFG_PATH.read_text(encoding='utf-8'))


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS seen (
            url TEXT PRIMARY KEY,
            source TEXT,
            title TEXT,
            published TEXT,
            stored_path TEXT,
            created_at TEXT
        )"""
    )
    return conn


def is_seen(conn, url: str) -> bool:
    cur = conn.execute("SELECT 1 FROM seen WHERE url=?", (url,))
    return cur.fetchone() is not None


def mark_seen(conn, url, source, title, published, stored_path):
    conn.execute(
        "INSERT OR IGNORE INTO seen(url,source,title,published,stored_path,created_at) VALUES(?,?,?,?,?,?)",
        (url, source, title, published, stored_path, dt.datetime.utcnow().isoformat() + 'Z'),
    )
    conn.commit()


def fetch_xml(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 OpenClawMonitor/1.0"})
    with urlopen(req, timeout=25) as r:
        return r.read().decode('utf-8', errors='ignore')


def sanitize(name: str) -> str:
    return re.sub(r'[^\w\-\. ]+', '', name, flags=re.UNICODE).strip().replace(' ', '_')[:80]


def slug(text: str) -> str:
    s = re.sub(r'[^\w\- ]+', '', text, flags=re.UNICODE).strip().lower()
    s = re.sub(r'\s+', '-', s)
    return s[:80] or hashlib.md5(text.encode()).hexdigest()[:10]


def relevance(text: str, keywords, min_hits: int):
    txt = (text or '').lower()
    hits = [k for k in keywords if k.lower() in txt]
    return ('high' if len(hits) >= min_hits else ('med' if hits else 'low'), hits)


def parse_rss_items(xml_text: str):
    items = []
    root = ET.fromstring(xml_text)
    for it in root.findall('.//item'):
        title = (it.findtext('title') or '').strip()
        link = (it.findtext('link') or '').strip()
        desc = (it.findtext('description') or '').strip()
        pub = (it.findtext('pubDate') or '').strip()
        if link:
            items.append({"title": title, "url": link, "summary": desc, "published": pub})
    return items


def parse_youtube_atom(xml_text: str):
    ns = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
    root = ET.fromstring(xml_text)
    items = []
    for e in root.findall('a:entry', ns):
        title = (e.findtext('a:title', default='', namespaces=ns) or '').strip()
        vid = (e.findtext('yt:videoId', default='', namespaces=ns) or '').strip()
        pub = (e.findtext('a:published', default='', namespaces=ns) or '').strip()
        upd = (e.findtext('a:updated', default='', namespaces=ns) or '').strip()
        link_el = e.find('a:link', ns)
        link = link_el.attrib.get('href') if link_el is not None else f'https://www.youtube.com/watch?v={vid}'
        summary = (e.findtext('a:content', default='', namespaces=ns) or '').strip()
        items.append({"title": title, "url": link, "summary": summary, "published": pub or upd, "video_id": vid})
    return items


def write_note(base_dir: Path, source_name: str, item: dict, rel: str, tags: list, source_type: str):
    day = dt.datetime.utcnow().date().isoformat()
    name = f"{day}__{slug(item.get('title','item'))}.md"
    p = base_dir / source_name
    p.mkdir(parents=True, exist_ok=True)
    fp = p / name
    content = f"""---
type: monitor-item
source_type: {source_type}
source_name: {source_name}
date: {day}
relevance: {rel}
tags: [{', '.join(tags[:6])}]
---

# {item.get('title','(no title)')}

## Source
- URL: {item.get('url','')}
- Published: {item.get('published','')}

## Summary
{(item.get('summary') or '').strip()[:1200]}

## Key points
- TBD

## Why it matters
- TBD

## Action/Idea
- TBD

## Fact vs Opinion
- hypothesis
"""
    fp.write_text(content, encoding='utf-8')
    return fp


def maybe_write_youtube_summary(item: dict, rel: str, source_name: str):
    if rel != 'high':
        return None
    day = dt.datetime.utcnow().date().isoformat()
    out_dir = VAULT / '20_Summaries'
    out_dir.mkdir(parents=True, exist_ok=True)
    fp = out_dir / f"{day}__youtube__{sanitize(source_name)}__{slug(item.get('title','video'))}.md"
    content = f"""---
type: youtube-summary
status: processed
date: {day}
relevance: high
source: {source_name}
---

# {item.get('title','')}

## Source
- URL: {item.get('url','')}
- Published: {item.get('published','')}

## Summary
{(item.get('summary') or '').strip()[:1500]}

## Notes
- High relevance item auto-promoted from monitor.
- Transcript/whisper step can be enabled later in config.
"""
    fp.write_text(content, encoding='utf-8')
    return fp


def run():
    cfg = load_cfg()
    conn = db()
    added = []

    # X via RSS (nitter or custom rss)
    x_cfg = cfg.get('x', {})
    x_urls = list(x_cfg.get('rss_urls', []))
    nitter = x_cfg.get('nitter_base', 'https://nitter.net').rstrip('/')
    for h in x_cfg.get('handles', []):
        handle = h.lstrip('@').strip()
        if handle:
            x_urls.append(f"{nitter}/{quote(handle)}/rss")

    for u in x_urls:
        try:
            xml = fetch_xml(u)
            items = parse_rss_items(xml)
        except Exception:
            continue
        for it in items[:15]:
            url = it.get('url')
            if not url or is_seen(conn, url):
                continue
            rel, hits = relevance((it.get('title','') + ' ' + it.get('summary','')), cfg.get('relevance_keywords', []), cfg.get('high_relevance_min_hits', 2))
            source_name = re.sub(r'https?://|/rss', '', u).split('/')[0] if '/rss' not in u else u.split('/')[-2]
            fp = write_note(VAULT / '10_Channels' / 'X', sanitize(source_name), it, rel, hits or ['x', 'monitor'], 'x')
            mark_seen(conn, url, 'x', it.get('title',''), it.get('published',''), str(fp))
            added.append(('x', str(fp)))

    # YouTube via official feeds
    y_cfg = cfg.get('youtube', {})
    y_urls = list(y_cfg.get('feed_urls', []))
    for cid in y_cfg.get('channel_ids', []):
        cid = cid.strip()
        if cid:
            y_urls.append(f"https://www.youtube.com/feeds/videos.xml?channel_id={quote(cid)}")

    for u in y_urls:
        try:
            xml = fetch_xml(u)
            items = parse_youtube_atom(xml)
        except Exception:
            continue
        source_name = 'youtube'
        m = re.search(r'channel_id=([^&]+)', u)
        if m:
            source_name = m.group(1)
        for it in items[:10]:
            url = it.get('url')
            if not url or is_seen(conn, url):
                continue
            rel, hits = relevance((it.get('title','') + ' ' + it.get('summary','')), cfg.get('relevance_keywords', []), cfg.get('high_relevance_min_hits', 2))
            fp = write_note(VAULT / '10_Channels' / 'YouTube', sanitize(source_name), it, rel, hits or ['youtube', 'monitor'], 'youtube')
            mark_seen(conn, url, 'youtube', it.get('title',''), it.get('published',''), str(fp))
            added.append(('youtube', str(fp)))
            maybe_write_youtube_summary(it, rel, sanitize(source_name))

    # Daily brief (max 5)
    day = dt.datetime.utcnow().date().isoformat()
    brief = VAULT / '20_Summaries' / f"{day}__daily-intelligence-brief.md"
    brief.parent.mkdir(parents=True, exist_ok=True)
    bullets = added[:5]
    lines = [f"# Daily Intelligence Brief — {day}", ""]
    if bullets:
        for src, p in bullets:
            lines.append(f"- [{src}] {p}")
    else:
        lines.append("- No high-value new items in this cycle.")
    brief.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    run()

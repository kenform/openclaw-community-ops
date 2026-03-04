#!/usr/bin/env python3
import datetime as dt
import json
import re
from pathlib import Path

VAULT = Path('/home/openclawuser/vault')
INBOX = VAULT / '00_Inbox'
SUMM = VAULT / '20_Summaries'
REPORT_DIR = Path('/home/openclawuser/.openclaw/workspace/tmp/obsidian-housekeeping')
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def norm_url(s: str):
    m = re.search(r'https?://\S+', s or '')
    return (m.group(0).rstrip(').,;!') if m else '').lower()


def first_title(text: str, fallback: str):
    for ln in text.splitlines():
        if ln.startswith('# '):
            return ln[2:].strip()
    return fallback


def normalize_tags(text: str):
    # lowercase and dedup hashtags
    tags = re.findall(r'(?<!\w)#([A-Za-zА-Яа-яЁё0-9_\-]+)', text)
    seen = []
    for t in tags:
        k = t.lower()
        if k not in seen:
            seen.append(k)
    if not seen:
        return text
    # append normalized tag line if absent
    if '## Tags' in text:
        text = re.sub(r'## Tags\n(?:.*\n)?', '## Tags\n' + ' '.join('#'+x for x in seen[:10]) + '\n', text, count=1)
    return text


def main():
    md_files = list(VAULT.rglob('*.md'))
    idx = {}
    dup_removed = 0
    tag_fixed = 0
    moved = 0

    for p in sorted(md_files):
        try:
            txt = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        title = first_title(txt, p.stem).lower().strip()
        url = norm_url(txt)
        key = (title, url)
        if key in idx and url:
            # remove duplicate file keeping first one
            try:
                p.unlink()
                dup_removed += 1
                continue
            except Exception:
                pass
        else:
            idx[key] = str(p)

        new_txt = normalize_tags(txt)
        if new_txt != txt:
            try:
                p.write_text(new_txt, encoding='utf-8')
                tag_fixed += 1
            except Exception:
                pass

        # simple move rule: if file under root and has #ready -> summaries
        if p.parent == VAULT and '#ready' in new_txt.lower():
            SUMM.mkdir(parents=True, exist_ok=True)
            np = SUMM / p.name
            try:
                p.rename(np)
                moved += 1
            except Exception:
                pass

    rpt = REPORT_DIR / f'weekly-{dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")}.md'
    rpt.write_text(
        f"# Obsidian Weekly Housekeeping\n"
        f"- scanned: {len(md_files)}\n"
        f"- duplicates removed: {dup_removed}\n"
        f"- tags normalized: {tag_fixed}\n"
        f"- moved to summaries: {moved}\n",
        encoding='utf-8'
    )
    print(rpt)


if __name__ == '__main__':
    main()

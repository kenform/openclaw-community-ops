#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path


def norm_text(s: str) -> str:
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    s = re.sub(r'[ \t]+$', '', s, flags=re.M)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip() + ('\n' if s.strip() else '')


def first_h1(text: str, fallback: str) -> str:
    for ln in text.splitlines():
        if ln.startswith('# '):
            return ln[2:].strip().lower()
    return fallback.lower().strip()


def body_for_hash(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return '\n'.join(lines[:40]).lower()


def key_for(text: str, stem: str) -> str:
    t = first_h1(text, stem)
    b = body_for_hash(text)
    return hashlib.sha1((t + '\n' + b).encode('utf-8', 'ignore')).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding='utf-8'))
    vault = Path(cfg['vault_path'])
    reports_dir = Path(cfg['reports_dir'])
    reports_dir.mkdir(parents=True, exist_ok=True)
    archive_rel = cfg.get('archive_dir', '90_MOC/auto-clean')
    archive_dir = vault / archive_rel
    archive_dir.mkdir(parents=True, exist_ok=True)

    min_chars = int(cfg.get('min_chars_keep', 40))
    dedupe_on = bool(cfg.get('dedupe', {}).get('enabled', True))

    report = {
        'ts': int(dt.datetime.now(dt.timezone.utc).timestamp()),
        'mode': 'obsidian_no_gpt_cleaner',
        'apply': bool(args.apply),
        'vault': str(vault),
        'scanned': 0,
        'normalized': 0,
        'archived_short': 0,
        'archived_duplicates': 0,
        'errors': 0,
        'items': []
    }

    seen = {}
    files = sorted([p for p in vault.rglob('*.md') if '.git/' not in str(p)])

    for p in files:
        report['scanned'] += 1
        try:
            txt = p.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            report['errors'] += 1
            report['items'].append({'file': str(p), 'action': 'read_error', 'error': type(e).__name__})
            continue

        original = txt
        cleaned = norm_text(txt)

        # normalize file if needed
        if cleaned != original:
            report['normalized'] += 1
            if args.apply:
                try:
                    p.write_text(cleaned, encoding='utf-8')
                except Exception as e:
                    report['errors'] += 1
                    report['items'].append({'file': str(p), 'action': 'write_error', 'error': type(e).__name__})
                    continue

        effective = cleaned
        # archive too-short notes
        if len(effective.strip()) < min_chars:
            target = archive_dir / p.name
            if target.exists():
                target = archive_dir / f"{p.stem}__{int(dt.datetime.now().timestamp())}{p.suffix}"
            report['archived_short'] += 1
            report['items'].append({'file': str(p), 'action': 'archive_short', 'to': str(target)})
            if args.apply:
                try:
                    p.rename(target)
                except Exception as e:
                    report['errors'] += 1
                    report['items'].append({'file': str(p), 'action': 'archive_short_error', 'error': type(e).__name__})
            continue

        # dedupe by title+body hash
        if dedupe_on:
            k = key_for(effective, p.stem)
            if k in seen:
                target = archive_dir / p.name
                if target.exists():
                    target = archive_dir / f"{p.stem}__dup__{int(dt.datetime.now().timestamp())}{p.suffix}"
                report['archived_duplicates'] += 1
                report['items'].append({'file': str(p), 'action': 'archive_duplicate', 'dup_of': seen[k], 'to': str(target)})
                if args.apply:
                    try:
                        p.rename(target)
                    except Exception as e:
                        report['errors'] += 1
                        report['items'].append({'file': str(p), 'action': 'archive_duplicate_error', 'error': type(e).__name__})
                continue
            seen[k] = str(p)

    out = reports_dir / f"obsidian_no_gpt_cleaner_{report['ts']}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'report': str(out), 'scanned': report['scanned'], 'normalized': report['normalized'], 'archived_short': report['archived_short'], 'archived_duplicates': report['archived_duplicates'], 'errors': report['errors']}, ensure_ascii=False))


if __name__ == '__main__':
    main()

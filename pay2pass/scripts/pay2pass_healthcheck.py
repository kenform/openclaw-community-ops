#!/usr/bin/env python3
import json, os, re, sqlite3, subprocess, time
from pathlib import Path

BASE=Path('/home/openclawuser/.openclaw/workspace/pay2pass')
DB=Path('/home/openclawuser/.openclaw/workspace/data/pay2pass_bridge.db')
LOG=BASE/'bridge.log'
REPORT_DIR=Path('/home/openclawuser/.openclaw/workspace/reports')
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def cmd(s):
    p=subprocess.run(s, shell=True, capture_output=True, text=True)
    return (p.stdout or '').strip()


def main():
    ts=int(time.time())
    procs=cmd("pgrep -af 'pay2pass_discord_bridge.py' | sed -n '1,20p'")
    rss=cmd("ps -o pid,rss,pcpu,etime,cmd -C python | grep pay2pass_discord_bridge.py | sed -n '1,5p'")
    db_counts={}
    if DB.exists():
        conn=sqlite3.connect(DB)
        cur=conn.cursor()
        for t in ['payments','subscriptions','link_codes']:
            try:
                db_counts[t]=cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
            except Exception:
                db_counts[t]=None
        conn.close()
    errors_last_200=0
    if LOG.exists():
        txt='\n'.join(LOG.read_text(encoding='utf-8', errors='ignore').splitlines()[-200:])
        errors_last_200=len(re.findall(r'error|traceback|exception', txt, re.I))
        # tiny log rotate
        if LOG.stat().st_size > 5*1024*1024:
            bak=BASE/f'bridge.log.{ts}.bak'
            LOG.rename(bak)
            LOG.write_text('', encoding='utf-8')
    report={
        'ts':ts,
        'mode':'pay2pass_healthcheck',
        'running': bool(procs.strip()),
        'process_lines': procs.splitlines() if procs else [],
        'rss_cpu': rss.splitlines() if rss else [],
        'db_counts': db_counts,
        'errors_last_200_lines': errors_last_200,
        'db_exists': DB.exists(),
        'log_exists': LOG.exists()
    }
    out=REPORT_DIR/f'pay2pass_healthcheck_{ts}.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'report':str(out), 'running':report['running'], 'errors_last_200_lines':errors_last_200}, ensure_ascii=False))

if __name__=='__main__':
    main()

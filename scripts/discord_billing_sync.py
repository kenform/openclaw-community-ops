#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import hmac
import json
import os
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request, error

DB_SCHEMA = '''
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  created_ts INTEGER NOT NULL,
  payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS subscriptions (
  discord_user_id TEXT NOT NULL,
  tier TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT,
  expires_at TEXT,
  last_event_id TEXT,
  updated_ts INTEGER NOT NULL,
  PRIMARY KEY (discord_user_id, tier)
);
'''


def load_env(path: str):
    if not path or not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#') or '=' not in ln:
                continue
            k, v = ln.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def db_conn(path: str):
    c = sqlite3.connect(path)
    c.executescript(DB_SCHEMA)
    c.commit()
    return c


def now_ts() -> int:
    return int(time.time())


def stripe_verify_signature(payload: bytes, sig_header: str, secret: str, tolerance: int = 300) -> bool:
    if not sig_header or not secret:
        return False
    parts = {}
    for item in sig_header.split(','):
        if '=' in item:
            k, v = item.split('=', 1)
            parts[k.strip()] = v.strip()
    t = parts.get('t')
    v1 = parts.get('v1')
    if not t or not v1:
        return False
    signed = f"{t}.".encode('utf-8') + payload
    expected = hmac.new(secret.encode('utf-8'), signed, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, v1):
        return False
    try:
        ts = int(t)
    except Exception:
        return False
    return abs(now_ts() - ts) <= tolerance


def discord_api(token: str, method: str, path: str, body: dict | None = None):
    url = f"https://discord.com/api/v10{path}"
    data = None
    headers = {
        'Authorization': f'Bot {token}',
        'User-Agent': 'openclaw-discord-billing-sync/1.0'
    }
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = request.Request(url, method=method, data=data, headers=headers)
    try:
        with request.urlopen(req, timeout=20) as r:
            raw = r.read().decode('utf-8')
            return r.status, json.loads(raw) if raw else {}
    except error.HTTPError as e:
        raw = e.read().decode('utf-8', errors='ignore') if hasattr(e, 'read') else ''
        return e.code, {'error': raw}


def send_mod_log(cfg: dict, text: str):
    ch = cfg.get('MOD_LOG_CHANNEL')
    if not ch:
        return
    discord_api(cfg['DISCORD_TOKEN'], 'POST', f"/channels/{ch}/messages", {'content': text[:1900]})


def role_for_tier(cfg: dict, tier: str) -> str | None:
    tier = (tier or '').lower()
    mapping = {
        'premium': cfg.get('ROLE_PREMIUM_MEMBER_ID'),
        'premium_member': cfg.get('ROLE_PREMIUM_MEMBER_ID'),
        'course_lifetime': cfg.get('ROLE_COURSE_LIFETIME_ID') or cfg.get('ROLE_PREMIUM_MEMBER_ID'),
        'vip': cfg.get('ROLE_VIP_MEMBER_ID'),
        'wt_vip': cfg.get('ROLE_WT_VIP_ID') or cfg.get('ROLE_VIP_MEMBER_ID'),
    }
    return mapping.get(tier) or cfg.get('ROLE_PREMIUM_MEMBER_ID')


def add_role(cfg: dict, discord_user_id: str, role_id: str):
    guild = cfg['GUILD_ID']
    return discord_api(cfg['DISCORD_TOKEN'], 'PUT', f"/guilds/{guild}/members/{discord_user_id}/roles/{role_id}")


def remove_role(cfg: dict, discord_user_id: str, role_id: str):
    guild = cfg['GUILD_ID']
    return discord_api(cfg['DISCORD_TOKEN'], 'DELETE', f"/guilds/{guild}/members/{discord_user_id}/roles/{role_id}")


def upsert_subscription(conn, discord_user_id: str, tier: str, status: str, expires_at: str | None, event_id: str):
    conn.execute(
        '''INSERT INTO subscriptions(discord_user_id,tier,status,started_at,expires_at,last_event_id,updated_ts)
           VALUES(?,?,?,?,?,?,?)
           ON CONFLICT(discord_user_id,tier) DO UPDATE SET
             status=excluded.status,
             expires_at=excluded.expires_at,
             last_event_id=excluded.last_event_id,
             updated_ts=excluded.updated_ts''',
        (discord_user_id, tier, status, dt.datetime.utcnow().isoformat(), expires_at, event_id, now_ts())
    )
    conn.commit()


def mark_event_once(conn, event_id: str, payload: dict) -> bool:
    try:
        conn.execute(
            'INSERT INTO events(event_id,created_ts,payload_json) VALUES(?,?,?)',
            (event_id, now_ts(), json.dumps(payload, ensure_ascii=False))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def parse_event_for_access(event: dict):
    et = event.get('type', '')
    obj = (((event.get('data') or {}).get('object')) or {})
    md = obj.get('metadata') or {}

    discord_user_id = str(md.get('discord_user_id') or md.get('discord_id') or '').strip()
    tier = str(md.get('tier') or md.get('plan') or 'premium').strip().lower()
    status = 'active'

    # expires_at may come from metadata directly
    expires_at = md.get('expires_at')

    if et in ('customer.subscription.deleted', 'invoice.payment_failed'):
        status = 'revoked'

    if not discord_user_id:
        return None
    return {
        'discord_user_id': discord_user_id,
        'tier': tier,
        'status': status,
        'expires_at': expires_at
    }


class StripeWebhookHandler(BaseHTTPRequestHandler):
    cfg = None
    db_path = None

    def _json(self, code: int, obj: dict):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == '/health':
            return self._json(200, {'ok': True, 'service': 'discord-billing-sync'})
        return self._json(404, {'ok': False})

    def do_POST(self):
        if self.path != '/webhook/stripe':
            return self._json(404, {'ok': False})

        ln = int(self.headers.get('Content-Length', '0'))
        payload = self.rfile.read(ln)
        sig = self.headers.get('Stripe-Signature', '')

        if not stripe_verify_signature(payload, sig, self.cfg['STRIPE_WEBHOOK_SECRET']):
            send_mod_log(self.cfg, '❌ Stripe webhook signature invalid')
            return self._json(400, {'ok': False, 'error': 'bad_signature'})

        try:
            event = json.loads(payload.decode('utf-8'))
        except Exception:
            return self._json(400, {'ok': False, 'error': 'bad_json'})

        event_id = str(event.get('id') or '')
        if not event_id:
            return self._json(400, {'ok': False, 'error': 'missing_event_id'})

        conn = db_conn(self.db_path)
        first_time = mark_event_once(conn, event_id, event)
        if not first_time:
            return self._json(200, {'ok': True, 'idempotent': True})

        parsed = parse_event_for_access(event)
        if not parsed:
            return self._json(200, {'ok': True, 'ignored': True})

        uid = parsed['discord_user_id']
        tier = parsed['tier']
        status = parsed['status']
        expires_at = parsed.get('expires_at')

        role_id = role_for_tier(self.cfg, tier)
        if not role_id:
            send_mod_log(self.cfg, f"⚠️ Unknown tier mapping: {tier}, user={uid}")
            return self._json(200, {'ok': True, 'warning': 'unknown_tier'})

        if status == 'active':
            code, _ = add_role(self.cfg, uid, role_id)
            send_mod_log(self.cfg, f"✅ Payment ok: user={uid}, tier={tier}, role={role_id}, code={code}")
        else:
            code, _ = remove_role(self.cfg, uid, role_id)
            send_mod_log(self.cfg, f"🛑 Access revoked: user={uid}, tier={tier}, role={role_id}, code={code}")

        upsert_subscription(conn, uid, tier, status, expires_at, event_id)
        conn.close()
        return self._json(200, {'ok': True})


def run_webhook(cfg: dict):
    host = cfg.get('BIND_HOST', '127.0.0.1')
    port = int(cfg.get('PORT', '8091'))
    StripeWebhookHandler.cfg = cfg
    StripeWebhookHandler.db_path = cfg['DATABASE']
    server = ThreadingHTTPServer((host, port), StripeWebhookHandler)
    print(json.dumps({'mode': 'webhook', 'listen': f'{host}:{port}', 'db': cfg['DATABASE']}, ensure_ascii=False))
    server.serve_forever()


def run_expiry_check(cfg: dict):
    conn = db_conn(cfg['DATABASE'])
    cur = conn.execute(
        "SELECT discord_user_id,tier,expires_at,status FROM subscriptions WHERE status='active' AND expires_at IS NOT NULL AND expires_at<>''"
    )
    today = dt.datetime.utcnow().date()
    processed = revoked = 0
    for uid, tier, exp, status in cur.fetchall():
        processed += 1
        try:
            exp_date = dt.date.fromisoformat(str(exp)[:10])
        except Exception:
            continue
        if exp_date < today:
            role_id = role_for_tier(cfg, tier)
            if role_id:
                code, _ = remove_role(cfg, uid, role_id)
                revoked += 1
                send_mod_log(cfg, f"⏰ Expiry revoke: user={uid}, tier={tier}, role={role_id}, code={code}")
            conn.execute(
                "UPDATE subscriptions SET status='expired', updated_ts=? WHERE discord_user_id=? AND tier=?",
                (now_ts(), uid, tier)
            )
    conn.commit()
    conn.close()
    print(json.dumps({'mode': 'expiry-check', 'processed': processed, 'revoked': revoked}, ensure_ascii=False))


def read_cfg(args):
    load_env(args.env_file)
    cfg = {
        'DISCORD_TOKEN': os.environ.get('DISCORD_TOKEN', '').strip(),
        'GUILD_ID': os.environ.get('GUILD_ID', '1484209988653027440').strip(),
        'STRIPE_WEBHOOK_SECRET': os.environ.get('STRIPE_WEBHOOK_SECRET', '').strip(),
        'DATABASE': os.environ.get('DATABASE', '/home/openclawuser/.openclaw/workspace/data/discord_billing.db').strip(),
        'MOD_LOG_CHANNEL': os.environ.get('MOD_LOG_CHANNEL', '123456789').strip(),
        'ROLE_PREMIUM_MEMBER_ID': os.environ.get('ROLE_PREMIUM_MEMBER_ID', '').strip(),
        'ROLE_VIP_MEMBER_ID': os.environ.get('ROLE_VIP_MEMBER_ID', '').strip(),
        'ROLE_COURSE_LIFETIME_ID': os.environ.get('ROLE_COURSE_LIFETIME_ID', '').strip(),
        'ROLE_WT_VIP_ID': os.environ.get('ROLE_WT_VIP_ID', '').strip(),
        'BIND_HOST': os.environ.get('BIND_HOST', '127.0.0.1').strip(),
        'PORT': os.environ.get('PORT', '8091').strip(),
    }
    os.makedirs(os.path.dirname(cfg['DATABASE']), exist_ok=True)
    missing = [k for k in ('DISCORD_TOKEN', 'STRIPE_WEBHOOK_SECRET') if not cfg.get(k)]
    if missing and args.mode == 'webhook':
        raise SystemExit(f"Missing required env: {', '.join(missing)}")
    return cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['webhook', 'expiry-check'], default='webhook')
    ap.add_argument('--env-file', default='/home/openclawuser/.openclaw/workspace/config/discord_billing.env')
    args = ap.parse_args()

    cfg = read_cfg(args)
    if args.mode == 'webhook':
        run_webhook(cfg)
    else:
        run_expiry_check(cfg)


if __name__ == '__main__':
    main()

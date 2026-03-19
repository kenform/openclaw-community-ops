#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import os
import secrets
import sqlite3
import time
from urllib import parse, request, error

DB_SCHEMA = '''
CREATE TABLE IF NOT EXISTS link_codes (
  code TEXT PRIMARY KEY,
  discord_id TEXT NOT NULL,
  tier TEXT NOT NULL,
  amount_usdt REAL NOT NULL,
  created_ts INTEGER NOT NULL,
  expires_ts INTEGER NOT NULL,
  used_ts INTEGER
);

CREATE TABLE IF NOT EXISTS payments (
  tx_hash TEXT PRIMARY KEY,
  from_address TEXT,
  to_address TEXT,
  amount_usdt REAL NOT NULL,
  token_symbol TEXT,
  block_ts INTEGER,
  confirmations INTEGER,
  tier TEXT,
  discord_id TEXT,
  status TEXT NOT NULL,
  created_ts INTEGER NOT NULL,
  processed_ts INTEGER
);

CREATE TABLE IF NOT EXISTS subscriptions (
  discord_id TEXT NOT NULL,
  tier TEXT NOT NULL,
  tx_hash TEXT,
  status TEXT NOT NULL,
  started_at TEXT,
  expires_at TEXT,
  updated_ts INTEGER NOT NULL,
  PRIMARY KEY (discord_id, tier)
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


def now_ts() -> int:
    return int(time.time())


def db(path: str):
    conn = sqlite3.connect(path)
    conn.executescript(DB_SCHEMA)
    conn.commit()
    return conn


def discord_api(token: str, method: str, path: str, body=None):
    url = f"https://discord.com/api/v10{path}"
    headers = {
        'Authorization': f'Bot {token}',
        'User-Agent': 'openclaw-pay2pass-bridge/1.0'
    }
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body).encode('utf-8')
    req = request.Request(url, method=method, data=data, headers=headers)
    try:
        with request.urlopen(req, timeout=20) as r:
            raw = r.read().decode('utf-8')
            return r.status, json.loads(raw) if raw else {}
    except error.HTTPError as e:
        raw = e.read().decode('utf-8', errors='ignore') if hasattr(e, 'read') else ''
        return e.code, {'error': raw}


def send_mod_log(cfg, text: str):
    ch = cfg.get('MOD_LOG_CHANNEL', '')
    if not ch:
        return
    discord_api(cfg['DISCORD_TOKEN'], 'POST', f"/channels/{ch}/messages", {'content': text[:1800]})


def role_for_tier(cfg, tier: str):
    t = (tier or '').lower()
    if t == 'premium':
        return cfg.get('ROLE_PREMIUM_MEMBER_ID')
    if t in ('mid', 'standard'):
        return cfg.get('ROLE_MID_MEMBER_ID')
    if t == 'vip':
        return cfg.get('ROLE_VIP_MEMBER_ID')
    return None


def add_role(cfg, discord_id: str, role_id: str):
    return discord_api(cfg['DISCORD_TOKEN'], 'PUT', f"/guilds/{cfg['GUILD_ID']}/members/{discord_id}/roles/{role_id}")


def remove_role(cfg, discord_id: str, role_id: str):
    return discord_api(cfg['DISCORD_TOKEN'], 'DELETE', f"/guilds/{cfg['GUILD_ID']}/members/{discord_id}/roles/{role_id}")


def bscscan_tokentx(cfg):
    qs = parse.urlencode({
        'module': 'account',
        'action': 'tokentx',
        'contractaddress': cfg['USDT_CONTRACT_ADDRESS'],
        'address': cfg['BLOCKCHAIN_ADDRESS'],
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'desc',
        'apikey': cfg['BSCSCAN_API_KEY'],
    })
    url = f"https://api.bscscan.com/api?{qs}"
    req = request.Request(url, headers={'User-Agent': 'openclaw-pay2pass-bridge/1.0'})
    with request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode('utf-8'))
    if str(data.get('status')) != '1':
        return []
    return data.get('result', [])


def classify_tier(cfg, amount_usdt: float):
    vip = float(cfg['VIP_PRICE_USDT'])
    mid = float(cfg['MID_PRICE_USDT'])
    premium = float(cfg['PREMIUM_PRICE_USDT'])
    if amount_usdt >= vip:
        return 'vip'
    if amount_usdt >= mid:
        return 'mid'
    if amount_usdt >= premium:
        return 'premium'
    return None


def process_tx(conn, cfg, tx):
    tx_hash = tx.get('hash')
    if not tx_hash:
        return

    exists = conn.execute('SELECT 1 FROM payments WHERE tx_hash=?', (tx_hash,)).fetchone()
    if exists:
        return

    to_addr = (tx.get('to') or '').lower()
    if to_addr != cfg['BLOCKCHAIN_ADDRESS'].lower():
        return

    symbol = (tx.get('tokenSymbol') or '').upper()
    if symbol != 'USDT':
        return

    raw = int(tx.get('value') or '0')
    decimals = int(tx.get('tokenDecimal') or '6')
    amount = raw / (10 ** decimals)
    tier = classify_tier(cfg, amount)

    conf = int(tx.get('confirmations') or '0')
    block_ts = int(tx.get('timeStamp') or '0')

    conn.execute(
        '''INSERT INTO payments(tx_hash,from_address,to_address,amount_usdt,token_symbol,block_ts,confirmations,tier,discord_id,status,created_ts)
           VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
        (tx_hash, (tx.get('from') or '').lower(), to_addr, amount, symbol, block_ts, conf, tier, None, 'received', now_ts())
    )
    conn.commit()

    if conf < int(cfg['MIN_CONFIRMATIONS']):
        return

    if not tier:
        send_mod_log(cfg, f"⚠️ Payment below minimum tier: tx={tx_hash[:10]} amount={amount:.6f} USDT")
        conn.execute('UPDATE payments SET status=?, processed_ts=? WHERE tx_hash=?', ('ignored', now_ts(), tx_hash))
        conn.commit()
        return

    # Match pending link code by exact tier and most recent not used
    row = conn.execute(
        '''SELECT code, discord_id, amount_usdt FROM link_codes
           WHERE tier=? AND used_ts IS NULL AND expires_ts>=?
           ORDER BY created_ts DESC LIMIT 1''',
        (tier, now_ts())
    ).fetchone()

    if not row:
        send_mod_log(cfg, f"⚠️ No pending link-code for tier={tier}, tx={tx_hash[:10]}, amount={amount:.4f} USDT")
        conn.execute('UPDATE payments SET status=?, processed_ts=? WHERE tx_hash=?', ('unmatched', now_ts(), tx_hash))
        conn.commit()
        return

    code, discord_id, expected_amount = row
    role_id = role_for_tier(cfg, tier)
    if not role_id:
        send_mod_log(cfg, f"❌ Missing role mapping for tier={tier}")
        return

    code_http, _ = add_role(cfg, discord_id, role_id)
    ok = 200 <= int(code_http) < 300

    conn.execute('UPDATE link_codes SET used_ts=? WHERE code=?', (now_ts(), code))
    conn.execute('UPDATE payments SET status=?, discord_id=?, processed_ts=? WHERE tx_hash=?',
                 ('role_granted' if ok else 'role_error', discord_id, now_ts(), tx_hash))

    expires_at = (dt.datetime.utcnow() + dt.timedelta(days=30)).isoformat()
    conn.execute(
        '''INSERT INTO subscriptions(discord_id,tier,tx_hash,status,started_at,expires_at,updated_ts)
           VALUES(?,?,?,?,?,?,?)
           ON CONFLICT(discord_id,tier) DO UPDATE SET
             tx_hash=excluded.tx_hash,
             status=excluded.status,
             started_at=excluded.started_at,
             expires_at=excluded.expires_at,
             updated_ts=excluded.updated_ts''',
        (discord_id, tier, tx_hash, 'active' if ok else 'error', dt.datetime.utcnow().isoformat(), expires_at, now_ts())
    )
    conn.commit()

    send_mod_log(cfg, f"✅ role {'granted' if ok else 'failed'}: user={discord_id}, tier={tier}, amount={amount:.4f} USDT, tx={tx_hash[:10]}")


def run_poll(cfg):
    conn = db(cfg['DATABASE'])
    send_mod_log(cfg, '🚀 pay2pass bridge polling started')
    while True:
        try:
            txs = bscscan_tokentx(cfg)
            for tx in txs[:100]:
                process_tx(conn, cfg, tx)
        except Exception as e:
            send_mod_log(cfg, f"❌ polling error: {type(e).__name__}: {e}")
        time.sleep(int(cfg['POLLING_INTERVAL_SECONDS']))


def run_expiry(cfg):
    conn = db(cfg['DATABASE'])
    today = dt.datetime.utcnow()
    rows = conn.execute(
        "SELECT discord_id,tier,expires_at,status FROM subscriptions WHERE status='active'"
    ).fetchall()
    revoked = 0
    for discord_id, tier, expires_at, status in rows:
        try:
            exp = dt.datetime.fromisoformat(expires_at)
        except Exception:
            continue
        if exp < today:
            role = role_for_tier(cfg, tier)
            if role:
                remove_role(cfg, discord_id, role)
            conn.execute("UPDATE subscriptions SET status='expired', updated_ts=? WHERE discord_id=? AND tier=?",
                         (now_ts(), discord_id, tier))
            revoked += 1
    conn.commit()
    send_mod_log(cfg, f"⏰ expiry check done: revoked={revoked}")
    print(json.dumps({'mode': 'expiry-check', 'revoked': revoked}, ensure_ascii=False))


def create_link(cfg, discord_id: str, tier: str):
    conn = db(cfg['DATABASE'])
    tier = tier.lower().strip()
    amount_map = {
        'premium': float(cfg['PREMIUM_PRICE_USDT']),
        'mid': float(cfg['MID_PRICE_USDT']),
        'vip': float(cfg['VIP_PRICE_USDT']),
    }
    if tier not in amount_map:
        raise SystemExit('tier must be premium|mid|vip')
    code = 'LINK_' + secrets.token_hex(4).upper()
    ttl = int(cfg['LINK_CODE_TTL_SECONDS'])
    conn.execute(
        'INSERT INTO link_codes(code,discord_id,tier,amount_usdt,created_ts,expires_ts) VALUES(?,?,?,?,?,?)',
        (code, discord_id, tier, amount_map[tier], now_ts(), now_ts() + ttl)
    )
    conn.commit()
    out = {
        'code': code,
        'discord_id': discord_id,
        'tier': tier,
        'amount_usdt': amount_map[tier],
        'address': cfg['BLOCKCHAIN_ADDRESS'],
        'network': cfg['BLOCKCHAIN_NETWORK'],
        'expires_in_sec': ttl,
    }
    print(json.dumps(out, ensure_ascii=False))


def load_cfg(env_file: str):
    load_env(env_file)
    cfg = {
        'DISCORD_TOKEN': os.environ.get('DISCORD_TOKEN', '').strip(),
        'GUILD_ID': os.environ.get('GUILD_ID', '1484209988653027440').strip(),
        'MOD_LOG_CHANNEL': os.environ.get('MOD_LOG_CHANNEL', '').strip(),
        'ROLE_PREMIUM_MEMBER_ID': os.environ.get('ROLE_PREMIUM_MEMBER_ID', '').strip(),
        'ROLE_MID_MEMBER_ID': os.environ.get('ROLE_MID_MEMBER_ID', '').strip(),
        'ROLE_VIP_MEMBER_ID': os.environ.get('ROLE_VIP_MEMBER_ID', '').strip(),
        'DATABASE': os.environ.get('DATABASE', '/home/openclawuser/.openclaw/workspace/data/pay2pass_bridge.db').strip(),
        'BLOCKCHAIN_ADDRESS': os.environ.get('BLOCKCHAIN_ADDRESS', '0x694bf4e92113d6d92216c532326ffb1bb6e2dab3').strip(),
        'BLOCKCHAIN_NETWORK': os.environ.get('BLOCKCHAIN_NETWORK', 'bsc').strip(),
        'USDT_CONTRACT_ADDRESS': os.environ.get('USDT_CONTRACT_ADDRESS', '0x55d398326f99059fF775485246999027B3197955').strip(),
        'BSCSCAN_API_KEY': os.environ.get('BSCSCAN_API_KEY', '').strip(),
        'POLLING_INTERVAL_SECONDS': os.environ.get('POLLING_INTERVAL_SECONDS', '10').strip(),
        'MIN_CONFIRMATIONS': os.environ.get('MIN_CONFIRMATIONS', '1').strip(),
        'PREMIUM_PRICE_USDT': os.environ.get('PREMIUM_PRICE_USDT', '25').strip(),
        'MID_PRICE_USDT': os.environ.get('MID_PRICE_USDT', '69').strip(),
        'VIP_PRICE_USDT': os.environ.get('VIP_PRICE_USDT', '150').strip(),
        'LINK_CODE_TTL_SECONDS': os.environ.get('LINK_CODE_TTL_SECONDS', '1800').strip(),
    }
    os.makedirs(os.path.dirname(cfg['DATABASE']), exist_ok=True)
    return cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['poll', 'expiry-check', 'create-link'], required=True)
    ap.add_argument('--env-file', default='/home/openclawuser/.openclaw/workspace/config/pay2pass_bridge.env')
    ap.add_argument('--discord-id')
    ap.add_argument('--tier')
    args = ap.parse_args()

    cfg = load_cfg(args.env_file)

    if args.mode == 'create-link':
        if not args.discord_id or not args.tier:
            raise SystemExit('--discord-id and --tier required for create-link')
        return create_link(cfg, args.discord_id, args.tier)

    if args.mode == 'expiry-check':
        return run_expiry(cfg)

    if not cfg.get('BSCSCAN_API_KEY'):
        raise SystemExit('BSCSCAN_API_KEY is required for polling mode')
    run_poll(cfg)


if __name__ == '__main__':
    main()

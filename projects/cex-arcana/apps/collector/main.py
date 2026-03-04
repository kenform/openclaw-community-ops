import os, time
import psycopg
from exchanges import bybit, bitget, mexc

DB=os.environ['DATABASE_URL']
INTERVAL=int(os.getenv('COLLECT_INTERVAL_SEC','45'))

INS_F='INSERT INTO funding_rates (ts,exchange,symbol,funding_rate) VALUES (%(ts)s,%(exchange)s,%(symbol)s,%(funding_rate)s) ON CONFLICT DO NOTHING'
INS_O='INSERT INTO open_interest (ts,exchange,symbol,oi_usd) VALUES (%(ts)s,%(exchange)s,%(symbol)s,%(oi_usd)s) ON CONFLICT DO NOTHING'
INS_V='INSERT INTO volumes (ts,exchange,symbol,volume_24h_usd) VALUES (%(ts)s,%(exchange)s,%(symbol)s,%(volume_24h_usd)s) ON CONFLICT DO NOTHING'

def loop():
    while True:
        rows=[bybit.fetch(), bitget.fetch(), mexc.fetch()]
        with psycopg.connect(DB) as c, c.cursor() as cur:
            for r in rows:
                cur.execute(INS_F, r['funding']); cur.execute(INS_O, r['oi']); cur.execute(INS_V, r['volume'])
        time.sleep(INTERVAL)

if __name__=='__main__':
    loop()

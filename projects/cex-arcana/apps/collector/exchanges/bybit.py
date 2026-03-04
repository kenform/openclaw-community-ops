import random, datetime as dt

def fetch(symbol='BTCUSDT'):
    now = dt.datetime.utcnow().isoformat() + 'Z'
    return {
      'funding': {'ts': now, 'exchange':'bybit','symbol':symbol,'funding_rate': random.uniform(-0.0005,0.0008)},
      'oi': {'ts': now, 'exchange':'bybit','symbol':symbol,'oi_usd': random.uniform(1e8,5e8)},
      'volume': {'ts': now, 'exchange':'bybit','symbol':symbol,'volume_24h_usd': random.uniform(5e8,2e9)},
    }

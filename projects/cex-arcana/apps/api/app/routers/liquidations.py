from fastapi import APIRouter
from ..db.conn import get_conn

router = APIRouter()

@router.get('/latest')
def latest(symbol: str = 'BTCUSDT'):
    qmap = {
      'funding':'SELECT * FROM funding_rates WHERE symbol=%s ORDER BY ts DESC LIMIT 20',
      'volume':'SELECT * FROM volumes WHERE symbol=%s ORDER BY ts DESC LIMIT 20',
      'oi':'SELECT * FROM open_interest WHERE symbol=%s ORDER BY ts DESC LIMIT 20',
      'liquidations':'SELECT * FROM liquidations WHERE symbol=%s ORDER BY ts DESC LIMIT 20',
      'arbitrage':'SELECT * FROM arb_signals WHERE symbol=%s ORDER BY ts DESC LIMIT 20',
    }
    table='liquidations'
    with get_conn() as c, c.cursor() as cur:
        cur.execute(qmap[table], (symbol,))
        rows = cur.fetchall()
    return {'symbol': symbol, 'rows': rows}

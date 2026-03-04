from .bybit import fetch as f

def fetch(symbol='BTCUSDT'):
    d=f(symbol); d['funding']['exchange']='bitget'; d['oi']['exchange']='bitget'; d['volume']['exchange']='bitget'; return d

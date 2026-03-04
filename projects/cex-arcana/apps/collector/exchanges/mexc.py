from .bybit import fetch as f

def fetch(symbol='BTCUSDT'):
    d=f(symbol); d['funding']['exchange']='mexc'; d['oi']['exchange']='mexc'; d['volume']['exchange']='mexc'; return d

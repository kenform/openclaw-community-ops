# CEX Arcana Architecture
- Collector (30-60s polling): Bybit/Bitget/MEXC
- TimescaleDB: time-series storage
- FastAPI: read API for dashboards/signals
- Next.js dashboard (next step)
- Arbitration service: funding spread + APR estimate

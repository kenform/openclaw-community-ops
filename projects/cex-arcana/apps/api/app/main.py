from fastapi import FastAPI
from .routers import funding, volume, oi, liquidations, arbitrage

app = FastAPI(title="CEX Arcana API")
app.include_router(funding.router, prefix="/funding", tags=["funding"])
app.include_router(volume.router, prefix="/volume", tags=["volume"])
app.include_router(oi.router, prefix="/oi", tags=["oi"])
app.include_router(liquidations.router, prefix="/liquidations", tags=["liquidations"])
app.include_router(arbitrage.router, prefix="/arbitrage", tags=["arbitrage"])

@app.get("/health")
def health():
    return {"ok": True}

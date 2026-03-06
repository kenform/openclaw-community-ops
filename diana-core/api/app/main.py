from fastapi import FastAPI
from datetime import datetime, timezone
import os

from app.db.session import Base, engine
from app.db import models  # noqa: F401

app = FastAPI(title="Diana Core API", version="0.1.0")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "diana-api",
        "env": os.getenv("APP_ENV", "unknown"),
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/version")
def version():
    return {
        "name": "diana-core",
        "version": "0.1.0",
    }

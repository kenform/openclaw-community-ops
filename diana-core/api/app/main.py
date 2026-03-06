from datetime import datetime, timezone
import os

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import Base, engine
from app.deps import get_db
from app.schemas import IngestMessageIn

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
    return {"name": "diana-core", "version": "0.1.0"}


@app.post("/ingest/message")
def ingest_message(payload: IngestMessageIn, db: Session = Depends(get_db)):
    if payload.role not in {"user", "assistant", "system"}:
        raise HTTPException(status_code=400, detail="role must be user|assistant|system")

    user = (
        db.query(models.User)
        .filter(models.User.external_id == payload.user_external_id)
        .first()
    )
    if not user:
        user = models.User(
            external_id=payload.user_external_id,
            display_name=payload.user_display_name,
        )
        db.add(user)
        db.flush()
    elif payload.user_display_name and user.display_name != payload.user_display_name:
        user.display_name = payload.user_display_name

    conv = (
        db.query(models.Conversation)
        .filter(
            models.Conversation.user_id == user.id,
            models.Conversation.channel == payload.channel,
            models.Conversation.chat_id == payload.chat_id,
        )
        .first()
    )
    if not conv:
        conv = models.Conversation(
            user_id=user.id,
            channel=payload.channel,
            chat_id=payload.chat_id,
        )
        db.add(conv)
        db.flush()

    msg = models.Message(
        conversation_id=conv.id,
        role=payload.role,
        content=payload.content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return {
        "ok": True,
        "message_id": msg.id,
        "conversation_id": conv.id,
        "user_id": user.id,
    }

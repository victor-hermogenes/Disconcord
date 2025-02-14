from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.models.chatModels import ChatMessage
from backend.app.models.userModels import User
from backend.app.core.database import get_db
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class ChatMessageResponse(BaseModel):
    username: str
    message: str
    timestamp: datetime 

    class Config:
        from_attributes = True

@router.get("/chat/{room_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(room_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .join(User)
        .filter(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "username": msg.user.username,
            "message": msg.message,
            "timestamp": msg.timestamp 
        }
        for msg in messages
    ]

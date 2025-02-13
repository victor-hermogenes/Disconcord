from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.chatModels import ChatMessage
from backend.app.models.userModels import User
from backend.app.models.roomModels import Room
from backend.app.services.authService import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Store active connections
active_connections = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user

@router.websocket("/ws/{room_id}")
async def chat_websocket(websocket: WebSocket, room_id: int, token: str):
    await websocket.accept()
    
    db = next(get_db())
    user = get_current_user(token, db)
    
    if room_id not in active_connections:
        active_connections[room_id] = []

    active_connections[room_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            new_message = ChatMessage(content=data, user_id=user.id, room_id=room_id)
            db.add(new_message)
            db.commit()

            # Broadcast message to all clients in the same room
            for conn in active_connections[room_id]:
                await conn.send_text(f"{user.username}: {data}")

    except WebSocketDisconnect:
        active_connections[room_id].remove(websocket)

@router.get("/{room_id}/messages", response_model=List[str])
def get_chat_messages(room_id: int, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.room_id == room_id).order_by(ChatMessage.timestamp.desc()).limit(50).all()
    return [f"{msg.user.username}: {msg.content}" for msg in messages]

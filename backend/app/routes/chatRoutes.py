from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.chatModels import ChatMessage
from backend.app.models.roomModels import Room
from backend.app.models.userModels import User
from backend.app.services.authService import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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

class MessageCreate(BaseModel):
    message: str

class MessageResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    message: str
    timestamp: str


@router.post("/{room_id}/send", response_model=MessageResponse)
def send_message(
    room_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Sala não encontrada")

    new_message = ChatMessage(
        room_id=room_id,
        user_id=current_user.id,
        message=message_data.message
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return new_message


@router.get("/{room_id}/messages", response_model=List[MessageResponse])
def get_messages(room_id: int, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.room_id == room_id).order_by(ChatMessage.timestamp).all()
    
    if not messages:
        return []

    return messages


active_connections = {}

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await websocket.accept()

    if room_id not in active_connections:
        active_connections[room_id] = []

    active_connections[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for connection in active_connections[room_id]:
                await connection.send_text(data)
    except WebSocketDisconnect:
        active_connections[room_id].remove(websocket)

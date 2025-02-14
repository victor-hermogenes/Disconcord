from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from backend.app.core.database import SessionLocal
from backend.app.models.roomModels import Room
from backend.app.models.userModels import User
from backend.app.services.authService import decode_access_token
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Set

router = APIRouter(prefix="/voice", tags=["Voice Chat"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

active_connections: Dict[int, Set[WebSocket]] = {} 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(websocket: WebSocket, db: Session):
    """Authenticate user via WebSocket token"""
    token = websocket.headers.get("Authorization")  
    
    if not token:
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail="Token não fornecido.")

    token = token.replace("Bearer ", "") 

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail="Token inválido ou expirado.")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user:
        await websocket.close(code=1008)
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return user

@router.websocket("/{room_id}")
async def voice_chat(websocket: WebSocket, room_id: int):
    async with get_db() as db:  
        user = await get_current_user(websocket, db)

        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            await websocket.close(code=1008)
            return

        await websocket.accept()

        if room_id not in active_connections:
            active_connections[room_id] = set()
        active_connections[room_id].add(websocket)

        try:
            while True:
                data = await websocket.receive_bytes()
                await broadcast_voice(room_id, websocket, data)
        except WebSocketDisconnect:
            active_connections[room_id].remove(websocket)
            if not active_connections[room_id]:  
                del active_connections[room_id]

async def broadcast_voice(room_id: int, sender_ws: WebSocket, data: bytes):
    for connection in active_connections.get(room_id, set()):
        if connection != sender_ws:
            await connection.send_bytes(data)

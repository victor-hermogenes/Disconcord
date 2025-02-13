from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from backend.app.core.database import SessionLocal
from backend.app.models.roomModels import Room
from backend.app.models.userModels import User
from backend.app.services.authService import decode_access_token
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/voice", tags=["Voice Chat"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

active_connections = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(websocket: WebSocket, db: Session):
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail="Token não fornecido.")

    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

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
    db = next(get_db())

    user = await get_current_user(websocket, db)
    
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    
    if room_id not in active_connections:
        active_connections.setdefault(room_id, {})[user.id] = websocket

    try:
        while True:
            data = await websocket.receive_bytes()
            await broadcast_voice(room_id, user.id, data)
    except WebSocketDisconnect:
        del active_connections[room_id][user.id]
        if not active_connections[room_id]:
            del active_connections[room_id]

async def broadcast_voice(room_id: int, sender_id: int, data: bytes):
    for user_id, connection in active_connections.get(room_id, {}).items():
        if user_id != sender_id:
            await connection.send_bytes(data)
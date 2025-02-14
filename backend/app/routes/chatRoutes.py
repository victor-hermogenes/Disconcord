from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.chatModels import ChatMessage
from backend.app.models.userModels import User
from backend.app.models.roomModels import Room
from backend.app.schemas.chatSchemas import ChatMessageResponse
from backend.app.services.authService import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from typing import List
import json
from urllib.parse import parse_qs

router = APIRouter(prefix="/chat", tags=["Chat"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

active_connections = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str, db: Session):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user

@router.websocket("/ws/{room_id}")
async def chat_websocket(websocket: WebSocket, room_id: int):
    await websocket.accept()

    db = next(get_db())  

    query_string = websocket.scope["query_string"].decode()
    params = parse_qs(query_string)
    token = params.get("token", [None])[0]  

    if not token:
        await websocket.close(code=1008)  
        return
    
    try:
        user = get_current_user(token, db)
    except HTTPException as e:
        await websocket.close(code=1008) 
        return

    if room_id not in active_connections:
        active_connections[room_id] = set()

    active_connections[room_id].add(websocket) 

    try:
        while True:
            data = await websocket.receive_text()

            try:
                parsed_data = json.loads(data)
                message_text = parsed_data.get("message", "").strip()
                
                if not message_text:
                    continue  
                
                new_message = ChatMessage(message=message_text, user_id=user.id, room_id=room_id)
                db.add(new_message)
                db.commit()

                broadcast_data = json.dumps({"username": user.username, "message": message_text})

                disconnected_clients = []
                for conn in active_connections[room_id]:
                    try:
                        await conn.send_text(broadcast_data)
                    except WebSocketDisconnect:
                        disconnected_clients.append(conn)

                for conn in disconnected_clients:
                    active_connections[room_id].remove(conn)

            except json.JSONDecodeError:
                await websocket.send_text("⚠️ Tipo inválido de mensagem. Esperado JSON.")

    except WebSocketDisconnect:
        active_connections[room_id].discard(websocket) 
        await websocket.close()
        print(f"👋 WebSocket disconnected: {user.username} from Room {room_id}")

@router.get("/{room_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(room_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .join(User)
        .filter(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(50)
        .all()
    )

    return [{"username": msg.user.username, "message": msg.message} for msg in messages]

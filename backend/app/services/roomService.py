from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
from backend.app.services.authService import decode_access_token

router = APIRouter(prefix="/chat", tags=["Chat"])

active_connections: List[WebSocket] = []

async def get_current_user(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)  
        return None
    
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008)  
        return None
    
    return payload.get("sub")  

@router.websocket("/room/{room_id}")
async def chat_endpoint(websocket: WebSocket, room_id: int):
    username = await get_current_user(websocket)
    if not username:
        return  

    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            message = await websocket.receive_text()
            for connection in active_connections:
                if connection != websocket: 
                    await connection.send_text(f"{username}: {message}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)

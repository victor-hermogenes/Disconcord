from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.authRoutes import router as auth_router
from backend.app.routes.usersRoutes import router as users_router
from backend.app.routes.roomsRoutes import router as rooms_router
from backend.app.routes.voiceRoutes import router as voice_router
from backend.app.routes.chatRoutes import router as chat_router
from typing import Optional

app = FastAPI(
    title="Disconcord API",
    version="1.0.0",
    description="A Discord Clone API with WebSockets and Authentication"
)

app.mount("/static", StaticFiles(directory="frontend/src/services"), name="static")
templates = Jinja2Templates(directory="frontend/src/pages") 

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(rooms_router)
app.include_router(voice_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/voice-chat-list")
async def voice_chat_list_page(request: Request):
    return templates.TemplateResponse("voice-chat-list.html", {"request": request}) 

@app.get("/voice-chat-room")
async def voice_chat_room_page(request: Request, roomId: Optional[int] = None):
    if roomId is None:
        return templates.TemplateResponse("voice-chat-room.html", {"request": request, "roomId": None})
    return templates.TemplateResponse("voice-chat-room.html", {"request": request, "roomId": roomId})
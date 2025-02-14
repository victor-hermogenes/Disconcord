from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import authRoutes, chatRoutes, usersRoutes, roomsRoutes, voiceRoutes
from backend.app.core.database import Base, engine_sync

Base.metadata.create_all(bind=engine_sync)

app = FastAPI(
    title="Disconcord API",
    description="Backend API for Disconcord, a lightweight communication platform.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authRoutes.router)
app.include_router(chatRoutes.router)
app.include_router(usersRoutes.router)
app.include_router(roomsRoutes.router)
app.include_router(voiceRoutes.router)

@app.get("/", tags=["Health Check"])
def root():
    return {"message": "Disconcord API is running!"}

from fastapi import FastAPI
from backend.app.controllers.auth_routes import router as auth_router

app = FastAPI(title="Disconcord API", version="1.0.0", description="A Discord Clone API")

app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "Bem-vindo ao Disconcord!"}


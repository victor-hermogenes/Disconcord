from fastapi import FastAPI
from backend.app.routes.authRoutes import router as auth_router
from backend.app.routes.usersRoutes import router as users_router

app = FastAPI(title="Disconcord API", version="1.0.0", description="A Discord Clone API")

app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
def home():
    return {"message": "Bem-vindo ao Disconcord!"}


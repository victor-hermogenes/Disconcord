from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from backend.app.core.database import SessionLocal
from backend.app.models.userModels import User
from backend.app.models.userLoginModels import UserLogin
from backend.app.models.userRegisterModels import UserRegister
from backend.app.services.authService import (
    hash_password, verify_password, create_access_token, decode_access_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário ou e-mail já está em uso.")

    hashed_password = hash_password(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, password_hash=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "usuário registrdao com sucesso.",
        "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    }


@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Logs in user using JSON payload."""
    user = db.query(User).filter(User.username == user_data.username).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    access_token = create_access_token({"sub": user.username}, expires_delta=timedelta(minutes=30))

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Deslogou com sucesso."}


@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token expirado ou inválido.")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return {"id": user.id, "username": user.username, "email": user.email}

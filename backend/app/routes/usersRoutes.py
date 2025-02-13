from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from backend.app.core.database import SessionLocal
from backend.app.models.userModels import User
from backend.app.services.userService import UserUpdate, UserResponse
from backend.app.services.authService import hash_password, decode_access_token

router = APIRouter(prefix="/users", tags=["Users"])
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
        raise HTTPException(status_code=401, detail="Token expirado ou inválido.")
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    return user

@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return user

@router.put("/{user_id}")
def update_user(
    user_id: int,
    email: str = Form(None),
    password: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user email and password using form-data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    if current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Não autorizado.")

    if email:
        user.email = email
    if password:
        user.password_hash = hash_password(password)

    db.commit()
    db.refresh(user)
    return {"message": "Usuário atualizado com sucesso."}

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    if current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Não autorizado.")

    db.delete(user)
    db.commit()
    return {"message": "Usuário deletado com sucesso."}

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.userModels import User
from backend.app.schemas.userSchema import UserCreate, UserUpdate, UserResponse
from backend.app.services.authService import hash_password

def get_user_by_id(db: Session, user_id: int) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user

def get_user_by_username(db: Session, username: str) -> UserResponse:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user

def create_user(db: Session, user_data: UserCreate) -> UserResponse:
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário ou e-mail já cadastrado")

    hashed_password = hash_password(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, password_hash=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def update_user(db: Session, user_id: int, user_data: UserUpdate, current_user: User) -> UserResponse:
    user = get_user_by_id(db, user_id)

    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado")

    if user_data.email:
        user.email = user_data.email
    if user_data.password:
        user.password_hash = hash_password(user_data.password)

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int, current_user: User):
    user = get_user_by_id(db, user_id)

    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado")

    db.delete(user)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}

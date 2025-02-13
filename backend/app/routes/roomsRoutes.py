from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.roomModels import Room
from backend.app.models.userModels import User
from backend.app.services.roomService import RoomCreate, RoomUpdate, RoomResponse
from backend.app.services.authService import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

router = APIRouter(prefix="/rooms", tags=["Rooms"])
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
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user


class RoomCreateRequest(BaseModel):
    name: str


class RoomUpdateRequest(BaseModel):
    name: str | None = None


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_room = db.query(Room).filter(Room.name == room_data.name).first()
    if existing_room:
        raise HTTPException(status_code=400, detail="Nome da sala já está em uso")

    new_room = Room(name=room_data.name, owner_id=current_user.id)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


@router.get("/", response_model=list[RoomResponse])
def get_all_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_data: RoomUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    if room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado")

    if room_data.name:
        room.name = room_data.name

    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    
    if room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado")

    db.delete(room)
    db.commit()
    return {"message": "Sala deletada com sucesso"}

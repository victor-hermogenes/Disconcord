from pydantic import BaseModel

class RoomCreate(BaseModel):
    name: str

class RoomUpdate(BaseModel):
    name: str | None = None

class RoomResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    class Config:
        from_attributes = True

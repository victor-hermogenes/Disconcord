from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RoomBase(BaseModel):
    name: str

class RoomCreate(RoomBase):
    rtc_session_id: Optional[str] = None

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    rtc_session_id: Optional[str] = None

class RoomResponse(RoomBase):
    id: int
    owner_id: int
    created_at: datetime
    rtc_session_id: Optional[str] = None

    class Config:
        from_attributes = True 

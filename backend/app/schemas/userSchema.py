from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

class UserResponse(UserBase):
    id: int = Field(..., gt=0) 
    created_at: datetime

    class Config:
        from_attributes = True

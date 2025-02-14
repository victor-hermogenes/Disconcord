from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(32), unique=True, nullable=False, index=True) 
    email = Column(String(128), unique=True, nullable=True, index=True) 
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    rooms = relationship("Room", back_populates="owner", cascade="all, delete-orphan", lazy="joined")
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan", lazy="joined")
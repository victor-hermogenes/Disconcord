from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from backend.app.core.config import settings 

engine_async = create_async_engine(
    settings.DATABASE_URL_ASYNC, 
    future=True, 
    echo=True,
    pool_size=20, 
    max_overflow=5
)

engine_sync = create_engine(
    settings.DATABASE_URL_SYNC, 
    future=True, 
    echo=True,
    pool_size=20, 
    max_overflow=5
)

AsyncSessionLocal = sessionmaker(bind=engine_async, class_=AsyncSession, expire_on_commit=False)

SessionLocal = sessionmaker(bind=engine_sync, autocommit=False, autoflush=False)

Base = declarative_base()

from backend.app.models import userModels, roomModels, chatModels

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
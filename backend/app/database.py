from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

dotenvPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"scripts/.env")
load_dotenv(dotenvPath, override=True)

DATA_BASE_ASYNC  = os.getenv("DATABASE_URL")

if not DATA_BASE_ASYNC:
    raise ValueError("DATABASE_URL não encontrado no .env, cheque o arquivo.")

print("DATABASE_URL carregado: ", DATA_BASE_ASYNC)

DATA_BASE_SYNC = DATA_BASE_ASYNC.replace("+asyncpg", "") if DATA_BASE_ASYNC else None

if not DATA_BASE_SYNC:
    raise ValueError("DATABASE_URL_SYNC é invalido! Cheque suas configurações do .env.")

engine_async = create_async_engine(DATA_BASE_ASYNC, future=True, echo=True)
engine_sync = create_engine(DATA_BASE_SYNC, future=True, echo=True)

AsyncSessionLocal = sessionmaker(bind=engine_async, class_=AsyncSession, expire_on_commit=False)
SessionLocal = sessionmaker(bind=engine_sync, autocommit=False, autoflush=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal as session:
        yield session
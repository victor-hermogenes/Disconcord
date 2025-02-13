import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(dotenv_path, override=True)

class Settings:
    PROJECT_NAME: str = "Disconcord API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Made in 3 days"

    DATABASE_URL_ASYNC: str = os.getenv("DATABASE_URL")
    DATABASE_URL_SYNC: str = DATABASE_URL_ASYNC.replace("+asyncpg", "") if DATABASE_URL_ASYNC else None

    if not DATABASE_URL_ASYNC or not DATABASE_URL_SYNC:
        raise ValueError("⚠️ Faltando .env em DATABASE_URL. Cheque sua configuração.")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

    MAX_CONNECTIONS: int = int(os.getenv("MAX_CONNECTIONS", 100))

settings = Settings()
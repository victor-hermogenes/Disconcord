import logging
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from backend.app.core.key_manager import get_current_key
from backend.app.core.config import settings 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = get_current_key()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=TOKEN_EXPIRATION_MINUTES))
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"🔐 Access token criado para usuário: {data.get('sub')}")
    return token

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logger.warning(f"⚠️ JWT decoding falhou: {e}")
        return None

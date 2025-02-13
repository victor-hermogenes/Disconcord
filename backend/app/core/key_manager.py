import os
import secrets
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key, dotenv_values
from backend.app.core.config import settings 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROTATION_INTERVAL_HOURS = int(settings.KEY_ROTATION_INTERVAL_HOURS)

load_dotenv(settings.DOTENV_PATH)

def generate_key():
    """Generate a new 32-byte hex token as a secret key."""
    return secrets.token_hex(32)

def rotate_keys():
    """Rotates SECRET_KEY in the `.env` file if needed."""
    env_vars = dotenv_values(settings.DOTENV_PATH) 
    last_rotation = env_vars.get("LAST_KEY_ROTATION")

    if last_rotation:
        last_rotation = datetime.fromisoformat(last_rotation)
    else:
        last_rotation = datetime.utcnow() - timedelta(hours=ROTATION_INTERVAL_HOURS + 1)

    if datetime.utcnow() - last_rotation > timedelta(hours=ROTATION_INTERVAL_HOURS):
        new_key = generate_key()
        prev_key = env_vars.get("SECRET_KEY", "")

        # Update .env file
        set_key(settings.DOTENV_PATH, "PREVIOUS_SECRET_KEY", prev_key)
        set_key(settings.DOTENV_PATH, "SECRET_KEY", new_key)
        set_key(settings.DOTENV_PATH, "LAST_KEY_ROTATION", datetime.utcnow().isoformat())

        logger.info("🔑 SECRET_KEY resetada com sucesso!")

def get_current_key():
    rotate_keys()
    return dotenv_values(settings.DOTENV_PATH).get("SECRET_KEY", "")

def get_previous_key():
    return dotenv_values(settings.DOTENV_PATH).get("PREVIOUS_SECRET_KEY", "")

if __name__ == "__main__":
    rotate_keys()
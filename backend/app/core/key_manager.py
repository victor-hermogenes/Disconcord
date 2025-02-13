import os
import secrets
from datetime import datetime, timedelta

DOTENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env")

ROTATION_INTERVAL_HOURS = int(os.getenv("KEY_ROTATION_INTERVAL_HOURS", 24))

def generate_key():
    return secrets.token_hex(32)

def load_env():
    if not os.path.exists(DOTENV_PATH):
        return {}

    with open(DOTENV_PATH, "r") as file:
        lines = file.readlines()

    env_vars = {}
    for line in lines:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            env_vars[key] = value.strip("'").strip('"')
    return env_vars

def save_env(env_vars):
    with open(DOTENV_PATH, "w") as file:
        for key, value in env_vars.items():
            file.write(f"{key}='{value}'\n")

def rotate_keys():
    env_vars = load_env()
    last_rotation = env_vars.get("LAST_KEY_ROTATION", None)
    
    if last_rotation:
        last_rotation = datetime.fromisoformat(last_rotation)
    else:
        last_rotation = datetime.utcnow() - timedelta(hours=ROTATION_INTERVAL_HOURS + 1)

    if datetime.utcnow() - last_rotation > timedelta(hours=ROTATION_INTERVAL_HOURS):
        env_vars["PREVIOUS_SECRET_KEY"] = env_vars.get("SECRET_KEY", "")
        env_vars["SECRET_KEY"] = generate_key()
        env_vars["LAST_KEY_ROTATION"] = datetime.utcnow().isoformat()
        save_env(env_vars)
        print("SECRET_KEY rodada e atualizada em .env!")

def get_current_key():
    rotate_keys()
    return load_env().get("SECRET_KEY", "")

def get_previous_key():
    return load_env().get("PREVIOUS_SECRET_KEY", "")

if __name__ == "__main__":
    rotate_keys()

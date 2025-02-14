from pydantic import BaseModel, Field

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, regex="^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=6, max_length=128)

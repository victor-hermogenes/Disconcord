from pydantic import BaseModel, EmailStr, conint
from typing import Annotated

class UserRegister(BaseModel):
    username: Annotated[str, conint(min_length=3, max_length=32)] 
    email: EmailStr | None = None
    password: Annotated[str, conint(min_length=8, max_length=128)]

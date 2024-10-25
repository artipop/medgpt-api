from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(strict=True)
    
    username: str
    password_hash: bytes
    email: Optional[EmailStr] = None
    is_active: bool = True 
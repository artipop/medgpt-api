from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AuthCredentialsCreate(BaseModel):
    user_id: UUID
    auth_type: str
    password_hash: Optional[str] = None


class AuthCredentialsRead(AuthCredentialsCreate):
    id: UUID



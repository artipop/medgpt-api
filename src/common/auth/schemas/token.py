from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TokenFromIDProvider(BaseModel):
    token: str


class TokenCreate(BaseModel):
    user_id: UUID
    token: str


class TokenRead(BaseModel):
    user_id: UUID
    token: str
    created_at: datetime
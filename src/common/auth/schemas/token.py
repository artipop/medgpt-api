from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenFromIDProvider(BaseModel):
    token: str


class TokenCreate(BaseModel):
    user_id: UUID
    token: str
    token_type: str


class TokenRead(BaseModel):
    user_id: UUID
    token: str
    created_at: datetime
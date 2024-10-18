from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TokenCreate(BaseModel):
    user_id: UUID
    token: str


class TokenRead(BaseModel):
    user_id: UUID
    token: str
    created_at: datetime


class TokensRelationship(BaseModel):
    access_token_id: UUID
    refresh_token_id: UUID
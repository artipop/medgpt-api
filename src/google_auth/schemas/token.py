from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


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
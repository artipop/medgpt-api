from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    is_verified: bool

    class Config:
        from_attributes = True


class UserInDB(UserRead):
    password_hash: bytes = Field(..., min_length=6)


from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

from subs.schemas import SubscriptionData


class UserCreate(BaseModel):
    email: EmailStr


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    first_name: str | None = None
    second_name: str | None = None
    last_name: str | None = None
    is_verified: bool

    class Config:
        from_attributes = True


class UserSub(UserRead):
    subscription: SubscriptionData


class UserInDB(UserRead):
    password_hash: bytes = Field(..., min_length=6)


class Fullname(BaseModel):
    first_name: str | None = None
    second_name: str | None = None
    last_name: str | None = None

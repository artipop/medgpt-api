from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime


from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserInfoFromIDProvider(BaseModel):
    email: EmailStr


class OIDCUserCreate(BaseModel):
    email: EmailStr


class OIDCUserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime




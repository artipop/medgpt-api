from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class UserInfoFromIDProvider(BaseModel):
    name: str
    email: EmailStr

class OIDCUserCreate(BaseModel):
    email: EmailStr

class OIDCUserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime




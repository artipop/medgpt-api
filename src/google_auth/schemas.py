from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class UserFromProvider(BaseModel):
    email: EmailStr
    google_id: str = Field(alias="id")
    verified_email: bool
    name: str


class UserFromDB(BaseModel):
    id: str
    email: EmailStr



class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1)
    google_id: str = Field(min_length=1)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1)
    google_id: str = Field(min_length=1)
    

class UserDelete(BaseModel):
    id: UUID


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    google_id: Optional[str] = None
    created_at: datetime


class RefreshTokenCreate(BaseModel):
    user_id: UUID
    token: str = Field(min_length=1)
    expires_at: datetime


class RefreshTokenUpdate(BaseModel):
    token: Optional[str] = Field(None, min_length=1)
    expires_at: Optional[datetime] = None


class RefreshTokenDelete(BaseModel):
    id: UUID


class RefreshTokenResponse(BaseModel):
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    created_at: datetime


class UserWithRefreshTokensResponse(UserResponse):
    refresh_tokens: List[RefreshTokenResponse]



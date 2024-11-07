from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from uuid import UUID


class UserCreateBase(BaseModel):
    model_config = ConfigDict(strict=True)
    email: EmailStr


class UserCreatePlainPassword(UserCreateBase):
    password: str = Field(..., min_length=6)


class UserCreateHashedPassword(UserCreateBase):
    password_hash: bytes = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserFromToken(BaseModel):
    id: UUID = Field(alias="sub")
    email: EmailStr
    is_verified: bool


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    is_verified: bool

    class Config:
        from_attributes = True


class UserInDB(UserOut):
    password_hash: bytes = Field(..., min_length=6)
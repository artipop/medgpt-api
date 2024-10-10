from pydantic import BaseModel, Field, UUID4
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)


class UserDelete(BaseModel):
    id: UUID4


class UserResponse(BaseModel):
    id: UUID4
    name: str
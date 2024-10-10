from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_session
from google_auth.models import User, UserRepository
from google_auth.schemas import UserCreate, UserDelete, UserUpdate, UserResponse


router = APIRouter(
    prefix="/auth/google",
    tags=["google authorization"]
)


@router.get("/get_all", response_model=list[UserResponse])
async def get_all(session=Depends(get_session)):
    users: list[UserResponse] = await UserRepository(session).get_all()
    return users


@router.post("/create", response_model=UserResponse)
async def create_user(user: UserCreate, session=Depends(get_session)):
    created_user: UserResponse = await UserRepository(session).create(user)
    await UserRepository(session).commit()
    return created_user


@router.put("/update/{id}", response_model=UserResponse)
async def update_user(id: UUID, user: UserUpdate, session=Depends(get_session)):
    updated_user: UserResponse = await UserRepository(session).update_one(id, user)
    await UserRepository(session).commit()
    return updated_user


@router.delete("/delete/{id}", response_model=int)
async def delete_user(id: UUID, session=Depends(get_session)):
    rows: int = await UserRepository(session).delete_by_id(id)
    await UserRepository(session).commit()
    return rows



from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_session
from google_auth.models import User



router = APIRouter(
    prefix="/auth/google",
    tags=["google authorization"]
)

@router.get("/test_router")
async def say_hello():
    return {
        "status_code": 200,
        "payload": "Hello from FastAPI"
    }

@router.post("/post_data")
async def test_base_conn_write(name: str, session: AsyncSession = Depends(get_session)):
    new_user = User(name=name)
    
    session.add(new_user)
    await session.commit()
    
    return {
        "status_code": 200,
        "payload": "User created successfully",
        "user_id": new_user.id
    }

@router.get("/get_data")
async def test_base_conn_read(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()  # Get all user instances
    
    return {
        "status_code": 200,
        "payload": [user.name for user in users]
    }

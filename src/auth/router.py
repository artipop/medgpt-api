from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.get("/test_router")
async def say_hello():
    return {
        "status_code": 200,
        "payload": "Hello from FastAPT"
    }

from fastapi import APIRouter

router = APIRouter(
    prefix="/auth/native",
    tags=["native auhorization"]
)

@router.get("/test_router")
async def say_hello():
    return {
        "status_code": 200,
        "payload": "Hello from FastAPT"
    }

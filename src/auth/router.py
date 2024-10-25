from fastapi import APIRouter, Depends, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
from auth.utils.jwt_helpers import encode_jwt, decode_jwt 
from auth.schemas.user import User
from auth.schemas.token import TokenInfo
from auth.dependencies import valiadate_auth_user, get_current_active_auth_user
from auth.exceptions import NativeAuthException




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



@router.post("/login/")
async def auth_user_issue_jwt(
    user: User = Depends(valiadate_auth_user)
): 
    jwt_payload = {
        "sub": user.username, # rewrite to user_id
        "username": user.username,
        "email": user.email
    }
    
    
    token = encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )


@router.get("/users/me")
async def auth_user_check_self_info(
    user: User = Depends(get_current_active_auth_user)
):
    return user
from fastapi import APIRouter, Depends, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
from native_auth.utils.jwt_helpers import encode_jwt, decode_jwt 
from native_auth.schemas.token import TokenInfo
from native_auth.utils.password_helpers import hash_password
from native_auth.dependencies import (
    valiadate_auth_user, 
    get_current_active_auth_user, 
    get_current_auth_user_for_refresh
)
from database import get_session
from native_auth.utils.jwt_helpers import create_access_token, create_refresh_token
from native_auth.exceptions import NativeAuthException
from users.services.native_user_service import NativeUserService
from users.schemas.naitve_user_schemas import (
    UserCreatePlainPassword, 
    UserCreateHashedPassword, 
    UserLogin, 
    UserOut, 
    UserInDB
)

from pprint import pprint

router = APIRouter(
    prefix="/auth/native",
    tags=["native auhorization"]
)

@router.get("/test_router/", response_model=TokenInfo)
async def say_hello():
    return {
        "status_code": 200,
        "payload": "Hello from FastAPT"
    }


@router.post("/register/")
async def register_user(
    user_data: UserCreatePlainPassword,
    session=Depends(get_session) # TODO: add type hint
):
    # if user already exists, 401 exc will be raised 
    existing_user_data = await NativeUserService(session).check_user_existence_on_register(user_data)
    
    password_hash = hash_password(user_data.password)
    registred_user_data = await NativeUserService(session).create_user(
        UserCreateHashedPassword(
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash
        )
    )
    return registred_user_data
    

@router.post("/login/")
async def auth_user_issue_jwt(
    user: UserOut = Depends(valiadate_auth_user)
): 
    print(type(user))
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/users/me/")
async def auth_user_check_self_info(
    user: UserOut = Depends(get_current_active_auth_user)
):
    print(type(user))
    return user


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
def auth_refresh_jwt(
    user: UserOut = Depends(get_current_auth_user_for_refresh)
):
    access_token = create_access_token(user)

    return TokenInfo(
        access_token=access_token,
    )
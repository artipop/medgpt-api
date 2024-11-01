from typing import Dict
from enum import Enum
from users.schemas.naitve_user_schemas import (
    UserCreatePlainPassword, 
    UserCreateHashedPassword, 
    UserLogin, 
    UserOut,
    UserFromToken,
    UserInDB
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi import APIRouter, Depends, Form
from native_auth.utils.jwt_helpers import create_jwt, decode_jwt, TokenType, TOKEN_TYPE_FIELD
from native_auth.utils.password_helpers import hash_password, validate_password
from native_auth.exceptions import NativeAuthException
from settings import settings
from users.services.native_user_service import NativeUserService
from database import get_session
from pprint import pprint


http_bearer = HTTPBearer()

native_auth_scheme = OAuth2PasswordBearer(
    "/auth/native/login/"
)


async def valiadate_auth_user(
    username: str = Form(),
    password: str = Form(),
    # user: UserLogin,
    session=Depends(get_session)
):
    user = UserLogin(email=username, password=password)
    # TODO(weldonfe): if not user with provided email, raises 401 "No such user in DB"
    user_from_db: UserInDB = await NativeUserService(session).get_user_by_email(user_data=user)
    
    if not validate_password(
        password=user.password,
        password_hash=user_from_db.password_hash
    ): 
        raise NativeAuthException(detail="invalid username or password")
    
    if not user_from_db.is_active:
        raise NativeAuthException(detail="provided user is inactive")
    
    # explist cast required here
    user_out = UserOut.model_validate(user_from_db.model_dump(exclude={"password_hash"}))
    return user_out



def get_current_token_payload(
    token: str = Depends(native_auth_scheme)
) -> UserOut:
    payload = decode_jwt(token)
    return payload


def validate_token_type(payload: Dict, token_type: TokenType) -> bool:
    token_type_from_payload: TokenType = TokenType(payload.get(TOKEN_TYPE_FIELD))
    if token_type_from_payload == token_type:
        return True
    
    raise NativeAuthException(detail="invalid token type")


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    session=Depends(get_session)
):    
    validate_token_type(payload=payload, token_type=TokenType.ACCESS)

    user_from_token = UserFromToken(**payload)
    
    # NOTE raises 401 No such user in DB        
    user_from_db: UserInDB = await NativeUserService(session).get_user_by_id(user_data=user_from_token)
    
    return user_from_db


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_current_token_payload),
    session=Depends(get_session)
):
    validate_token_type(payload=payload, token_type=TokenType.REFRESH)
    
    user_from_token = UserFromToken(**payload)
    
    # NOTE raises 401 No such user in DB        
    user_from_db: UserInDB = await NativeUserService(session).get_user_by_id(user_data=user_from_token)
        
    return user_from_db


def get_current_active_auth_user(
    user: UserOut = Depends(get_current_auth_user)
):
    if not user.is_active:
        raise NativeAuthException(detail="Provided user is inactive")
    
    return user


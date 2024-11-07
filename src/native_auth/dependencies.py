from typing import Dict
from users.schemas.naitve_user_schemas import (
    UserLogin, 
    UserOut,
    UserFromToken,
    UserInDB
)
from fastapi import Depends, Request
from native_auth.utils.jwt_helpers import (
    decode_jwt, 
    TokenType, 
    TOKEN_TYPE_FIELD
)

from native_auth.utils.password_helpers import validate_password
from native_auth.exceptions import NativeAuthException
from settings import settings
from users.services.native_user_service import NativeUserService
from database import get_session
from common.auth.utils import get_auth_from_cookie
from pprint import pprint


async def authenticate(): pass


async def valiadate_auth_user(
    user: UserLogin,
    session=Depends(get_session)
):
    user = UserLogin(email=user.email, password=user.password)
    # TODO(weldonfe): if not user with provided email, raises 401 "No such user in DB"
    user_from_db: UserInDB = await NativeUserService(session).get_user_by_email(user_data=user)
    
    if not validate_password(
        password=user.password,
        password_hash=user_from_db.password_hash
    ): 
        raise NativeAuthException(detail="invalid username or password")
    
    if not user_from_db.is_verified: # TODO(weldonfe): how to handle that?
        raise NativeAuthException(detail="provided user is not verified")
    
    # explist cast required here
    user_out = UserOut.model_validate(user_from_db.model_dump(exclude={"password_hash"}))
    return user_out




def get_refresh_token_payload(
    token: str = Depends(get_auth_from_cookie)
):
    payload = decode_jwt(token)
    return payload


def get_access_token_payload(
    token: str = Depends(get_auth_from_cookie)
) -> UserOut:
    # unverefied_payload = decode_jwt_without_verification(token)
    payload = decode_jwt(token)
    return payload


def validate_token_type(payload: Dict, token_type: TokenType) -> bool:
    token_type_from_payload: TokenType = TokenType(payload.get(TOKEN_TYPE_FIELD))
    if token_type_from_payload == token_type:
        return True
    
    raise NativeAuthException(detail="invalid token type")


# NOTE: Main dependency to secure all buiseness routes
async def get_current_auth_user_by_access(
    payload: dict = Depends(get_access_token_payload),
    session=Depends(get_session)
):    
    validate_token_type(payload=payload, token_type=TokenType.ACCESS)

    user_from_token = UserFromToken(**payload)
    
    # NOTE raises 401 No such user in DB        
    user_from_db: UserInDB = await NativeUserService(session).get_user_by_id(user_data=user_from_token)
    
    return user_from_db


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_refresh_token_payload),
    session=Depends(get_session)
):
    validate_token_type(payload=payload, token_type=TokenType.REFRESH)
    
    user_from_token = UserFromToken(**payload)
    
    # NOTE raises 401 No such user in DB        
    user_from_db: UserInDB = await NativeUserService(session).get_user_by_id(user_data=user_from_token)
        
    
    return user_from_db


async def get_current_verified_auth_user(
    user: UserOut = Depends(get_current_auth_user_by_access)
):
    if not user.is_verified:
        raise NativeAuthException(detail="Provided user is inactive")
    
    return user


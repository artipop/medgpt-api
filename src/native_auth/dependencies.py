import jwt

from typing import Dict
from native_auth.schemas.user import (
    UserLogin, 
    UserOut,
    UserFromToken,
    UserInDB
)
from fastapi import Depends, Request, Response
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
from common.auth.utils import get_auth_from_cookie, decode_jwt_without_verification
from native_auth.utils.jwt_helpers import create_access_token
from pprint import pprint

from common.auth.services.auth_service import AuthService
from common.auth.exceptions import AuthException
from common.logger import logger


async def authenticate(id_token: str, response: Response, session=Depends(get_session)):
    try: 
        payload = decode_jwt(id_token)
    
    except AuthException as e:
        id_token = await refresh_token(id_token, response, session)

        response.set_cookie(
            key="session_id",
            value=f"Bearer {id_token}",
            httponly=True,  # to prevent JavaScript access
            secure=True,
        )

    logger.warning(payload)
    validate_token_type(payload=payload, token_type=TokenType.ID)
    
    logger.warning("TOKEN TYPE VALIDATION PASS")
    user_from_token: UserFromToken = UserFromToken(**payload)
    logger.warning("CAST TO USER FROM TOKEN PASS")


    user_from_db: UserOut = await AuthService(session).get_user_by_id(user_id=user_from_token.id)
    logger.warning("RECEIVING USER FROM DB PASS")

    if not user_from_db.is_verified:
        raise AuthException("User not verified")

    return user_from_db


async def valiadate_auth_user(
    user: UserLogin,
    session=Depends(get_session)
):
    user = UserLogin(email=user.email, password=user.password)
    # TODO(weldonfe): if not user with provided email, raises 401 "No such user in DB"
    user_from_db: UserInDB = await AuthService(session).get_native_user_by_mail(user_data=user)
    
    if not validate_password(
        password=user.password,
        password_hash=user_from_db.password_hash
    ): 
        raise NativeAuthException(detail="invalid username or password")
    
    if not user_from_db.is_verified: # TODO(weldonfe): how to handle that?
        raise AuthException("User not verified")
    
    # # explist cast required here
    user_out = UserOut.model_validate(user_from_db.model_dump(exclude={"password_hash"}))
    return user_out


async def refresh_token(id_token: str, response: Response, session):
    logger.critical("REFRESHING ID TOKEN")
    unverified_user_data = decode_jwt_without_verification(token=id_token)
    refresh_token = await AuthService(session).get_refresh_token_by_user_id(
        user_id=unverified_user_data.get("sub", "")
    )
    if not refresh_token:
        raise AuthException("No valid refresh token founded")
    
    try:
        payload = decode_jwt(id_token)
        
    except AuthException as e:
        await AuthService(session).delete_token_by_value(refresh_token)
        response.delete_cookie(
            key="session_id", 
            httponly=True, 
            secure=True
        )

        logger.critical(e)
        raise e
    
    id_token = create_access_token(
        UserFromToken(
            id=payload.get("sub"),
            email=payload.get("email"),
            is_verified=payload.get("is_verified"),
        )
    )
    return id_token


def validate_token_type(payload: Dict, token_type: TokenType) -> bool:
    token_type_from_payload: TokenType = TokenType(payload.get(TOKEN_TYPE_FIELD))
    if token_type_from_payload == token_type:
        return True
    
    raise AuthException(detail="invalid token type")


async def logout(
    id_token_payload: Dict, 
    session=Depends(get_session)
):
    deleted_tokens = await AuthService(session).logout_native_user(
        user_id=id_token_payload.get("sub", "")
    )
    
    
    





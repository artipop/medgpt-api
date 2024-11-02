import jwt
from settings import settings
from typing import Dict
from datetime import datetime, timezone, timedelta
from native_auth.exceptions import NativeAuthException
from enum import Enum
from users.schemas.naitve_user_schemas import (
    UserCreatePlainPassword, 
    UserCreateHashedPassword, 
    UserLogin, 
    UserOut, 
    UserInDB
)
import base64
from pprint import pprint

TOKEN_TYPE_FIELD = "type"

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def create_access_token(user: UserOut) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "email": user.email,
        "is_verified": user.is_verified,
    }
    return create_jwt(
        token_type=TokenType.ACCESS, 
        token_data=jwt_payload,
        
    )


def create_refresh_token(user: UserOut):
    jwt_payload = {
        "sub": str(user.id),
        "email": user.email,
        "is_verified": user.is_verified,
    }
    return create_jwt(token_type=TokenType.REFRESH, token_data=jwt_payload)


def create_jwt(
        token_type: TokenType, 
        token_data: dict
    ) -> str:
    
    jwt_payload = {"type": token_type.value}
    jwt_payload.update(token_data)
    
    expire_minutes = (
        settings.native_auth_jwt.access_token_expire_minutes 
        if token_type == TokenType.ACCESS
        else settings.native_auth_jwt.refresh_token_expire_minutes
    )
            
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes 
    )


def encode_jwt(
    payload: Dict,
    private_key: str = settings.native_auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.native_auth_jwt.algorithm,
    expire_minutes: int = settings.native_auth_jwt.access_token_expire_minutes
):
    to_encode = payload.copy()
    to_encode.update(
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc) + timedelta(minutes=expire_minutes),
    )

    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm
    )
    return encoded


def decode_jwt(
    token: str,
    public_key: str = settings.native_auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.native_auth_jwt.algorithm
):
    try: 
        # NOTE: expiration validation performed implicitly 
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=algorithm
        )
        
    except jwt.ExpiredSignatureError as e:
        raise NativeAuthException(
            detail = "token expired"
        )

    except jwt.InvalidTokenError as e:
        raise NativeAuthException(
            detail = "token validation failed"
        ) 
    
    return decoded


def decode_jwt_without_verification(token: str):
    print(f"!!! TOKEN: {token}")
    # decoded_payload = base64.urlsafe_b64decode(token).decode('utf-8')
    # print(decoded_payload)

    # decoded = jwt.decode(
    #     token, 
    #     options={
    #         "verify_signature": False 
    #     }
    # )
    # return decoded
    return token

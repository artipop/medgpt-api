import jwt
from settings import settings
from typing import Dict
from datetime import datetime, timezone, timedelta
from auth.exceptions import NativeAuthException


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

import jwt
from fastapi import Request
from enum import Enum
from common.auth.exceptions import AuthException
from settings import settings

class AuthScheme(Enum):
    GOOGLE = "https://accounts.google.com"
    NATIVE = settings.api_base_url


def determine_auth_scheme(token_payload: str) -> AuthScheme:
    issuer = token_payload.get("iss")
    if not issuer:
        raise AuthException("Auth token does not contain issuer")
    
    try: 
        return AuthScheme(issuer)
    
    except ValueError as e:
        raise AuthException("Unknown token issuer")


def get_auth_from_cookie(request: Request, cookie_name):
    authorization = request.cookies.get(cookie_name, "")
    scheme, separator, token = authorization.partition(" ")
    
    if not authorization or scheme.lower() != "bearer":
        raise AuthException("Invalid auth cookie")
    
    return token


def decode_jwt_without_verification(token: str):
    decoded = jwt.decode(
        token, 
        options={
            "verify_signature": False 
        }
    )
    return decoded

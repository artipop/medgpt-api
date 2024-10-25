from typing import Dict
from auth.schemas.user import User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi import APIRouter, Depends, Form
from auth.utils.jwt_helpers import encode_jwt, decode_jwt 
from auth.utils.password_helpers import hash_password, validate_password
from auth.exceptions import NativeAuthException

http_bearer = HTTPBearer()

native_auth_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/native/login/"
)

bob = User(
    username="Bob",
    password_hash=hash_password("qwerty"),
    email="johndoe@example.com"
)


alice = User(
    username="Alice",
    password_hash=hash_password("secret"),
    email="alice@example.com"
)

users_db: Dict[str, User] = {
    bob.username: bob,
    alice.username: alice 
}


def valiadate_auth_user(
    username: str = Form(),
    password: str = Form()
):
    if not (user := users_db.get(username)):
        raise NativeAuthException(detail="invalid username or password")
    
    if not validate_password(
        password=password,
        password_hash=user.password_hash
    ): 
        raise NativeAuthException(detail="invalid username or password")
    
    if not user.is_active:
        raise NativeAuthException(detail="invalid username or password")
        
    return user


def get_current_token_payload(
    # credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
    token: str = Depends(native_auth_scheme)
) -> User:
    # token = credentials.credentials
    payload = decode_jwt(token)
    return payload

def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload)
):
    username = payload.get("sub")
    if not (user := users_db.get(username)):
        raise NativeAuthException(detail="invalid username or password")
        
    return user


def get_current_active_auth_user(
    user: User = Depends(get_current_auth_user)
):
    if not user.is_active:
        raise NativeAuthException(detail="invalid username or password")
    
    return user
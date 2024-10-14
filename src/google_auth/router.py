import aiohttp
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select
from database import get_session
from google_auth.models import User, UserRepository
from google_auth.schemas import UserCreate, UserDelete, UserUpdate, UserResponse
from settings import settings
from jose import jwt
from common.logger import logger
from google_auth.dependencies import state_storage
from google_auth.utils.sequrity_requests import (
    exchage_code_to_tokens,
    get_user_info_from_provider,
    validate_id_token
)
from google_auth.utils.http_client import HttpClient
from google_auth.schemas import UserFromProvider
from pprint import pprint

router = APIRouter(
    prefix="/google-auth",
    tags=["google authorization"]
)


@router.get("/get_all", response_model=list[UserResponse])
async def get_all(session=Depends(get_session)):
    users: list[UserResponse] = await UserRepository(session).get_all()
    return users


@router.post("/create", response_model=UserResponse)
async def create_user(user: UserCreate, session=Depends(get_session)):
    created_user: UserResponse = await UserRepository(session).create(user)
    await UserRepository(session).commit()
    return created_user


@router.put("/update/{id}", response_model=UserResponse)
async def update_user(id: UUID, user: UserUpdate, session=Depends(get_session)):
    updated_user: UserResponse = await UserRepository(session).update_one(id, user)
    await UserRepository(session).commit()
    return updated_user


@router.delete("/delete/{id}", response_model=int)
async def delete_user(id: UUID, session=Depends(get_session)):
    rows: int = await UserRepository(session).delete_by_id(id)
    await UserRepository(session).commit()
    return rows


@router.get("/login", response_class=RedirectResponse)
async def redicrect_to_google_auth() -> str:
    """
        produces new state, to avoid csrf,
        encode it to jwt token,
        return url to redirect user to google oauth consent screen
    """
    jwt_token = state_storage.produce()
    return (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={settings.redirect_google_to_uri}&"
        f"scope=openid%20profile%20email&"
        f"&state={jwt_token}&"
        f"access_type=offline" # to get refresh token
    )


@router.get("/callback", response_class=RedirectResponse)
async def auth_callback(
    code: str,
    state: str = Depends(state_storage.validate),

    id_token_validation: bool = True
):    
    access_token, refresh_token, id_token = await exchage_code_to_tokens(code)
    if id_token_validation:
        # NOTE(weldonfe): that check might be unnecessary
        await validate_id_token(id_token, access_token)

    # NOTE(weldonfe): if we want to use header instead of cookie:
    # 1. rewrite here, to return access_token directly and change response type to str in route decorator
    # 2. change default transport method in google_auth.utils.security_handler.OpenIDConnectHandler
    response = RedirectResponse(url="/docs") # TODO(weldonfe): change redirection route to actual frontend
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {access_token}",
        httponly=True,  # to prevent JavaScript access
        secure=True,
    )
    return response


@router.get("/current_user_from_provider", response_model=UserFromProvider, status_code=200)
async def get_current_user_from_provider(user = Depends(get_user_info_from_provider)):
    return user
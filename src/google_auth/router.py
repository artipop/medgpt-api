import aiohttp
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from jose import jwt
from sqlalchemy.future import select
from database import get_session
from google_auth.models import User, UserRepository
from google_auth.schemas import UserCreate, UserDelete, UserUpdate, UserResponse
from settings import settings
from common.logger import logger
from pprint import pprint
from google_auth.dependencies import (
    get_http_client,
    oauth2_scheme, 
    state_storage,
)

router = APIRouter(
    prefix="/google-auth",
    tags=["google authorization"]
)

http_client = get_http_client()


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
        f"&state={jwt_token}"
    )


@router.get("/callback")
async def auth_callback(
    code: str,
    state: str = Depends(state_storage.validate),
    http_session: aiohttp.ClientSession = Depends(http_client.get_session)
):    
    # token exchange
    token_data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.redirect_google_to_uri,
        "grant_type": "authorization_code",
    }

    async with http_session.post(url=settings.google_token_url, 
                                 data=token_data) as resp:
        token_response_data = await resp.json()
        if resp.status != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
    access_token = token_response_data.get("access_token")
    
    # fetching user info
    headers = {"Authorization": f"Bearer {access_token}"}
    async with http_session.get(url=settings.google_userinfo_url,
                                headers=headers) as resp:
        user_info = await resp.json()
        logger.warning(user_info)

    return access_token


@router.get("/protected-endpoint-test")
async def test_auth(token: str = Depends(oauth2_scheme)):
    pprint(token)
    return {
        "payload": "protected_data"
    }
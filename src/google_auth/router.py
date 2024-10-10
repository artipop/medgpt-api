import aiohttp
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_session
from google_auth.models import User, UserRepository
from google_auth.schemas import UserCreate, UserDelete, UserUpdate, UserResponse
from settings import settings
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


ALGORITHM = "HS256"
SECRET_KEY = "my-secret-key"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REDIRECT_URI = "http://localhost:8888/google-auth/callback"
GOOGLE_CLIENT_ID = settings.google_client_id
GOOGLE_CLIENT_SECRET = settings.google_client_secret
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"


@router.get("/login/google")
async def login_google():
    state = "random_csrf_token"
    jwt_token = jwt.encode({"state": state}, SECRET_KEY, algorithm=ALGORITHM)
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&state={jwt_token}"
    }


@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get('code')
    jwt_token = request.query_params.get('state')
    # Verify the state (JWT)
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        state = payload.get("state")
        print(f"state: {state}")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid state token")
    # Exchange code for tokens
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    # token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url=GOOGLE_TOKEN_URL, data=token_data) as resp:
            print(resp.status)
            token_response_data = await resp.json()
            pprint(token_response_data)
    
    # token_response_data = token_response.json()
    
    if resp.status != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    access_token = token_response_data.get("access_token")
    # Use access token to fetch user info
    # user_info_response = requests.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=GOOGLE_USERINFO_URL) as resp:
            user_info = await resp.json()
            
    return user_info
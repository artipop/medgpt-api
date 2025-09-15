from fastapi import APIRouter, Depends, Response
from pydantic.v1 import EmailStr

from database import get_session

from native_auth.utils.jwt_helpers import create_access_token, create_refresh_token
from native_auth.utils.password_helpers import hash_password
from native_auth.dependencies import valiadate_auth_user, authenticate
from native_auth.schemas.user import UserCreatePlainPassword, UserCreateHashedPassword, UserChangePassword

from common.auth.services.auth_service import AuthService
from common.auth.schemas.token import TokenType
from common.auth.schemas.user import UserRead

router = APIRouter(
    prefix="/native-auth",
    tags=["native authorization"]
)


@router.post("/register/")
async def register_user(
    user_data: UserCreatePlainPassword,
    session=Depends(get_session) # TODO: add type hint
):
    # if user already exists, 401 exc will be raised 
    auth_service = AuthService(session)
    existing_user_data = await auth_service.check_user_existence_on_native_register(user_data)

    password_hash = hash_password(user_data.password)
    registred_user_data = await auth_service.register_native_user(
        UserCreateHashedPassword(
            email=user_data.email,
            password_hash=password_hash
        )
    )
    return registred_user_data


@router.put("/password")
async def change_password(
        data: UserChangePassword,
        session=Depends(get_session),
        user_data: UserRead = Depends(authenticate)
):
    auth_service = AuthService(session)
    password_hash = hash_password(data.new_password)
    registered_user_data = await auth_service.change_password(
        UserCreateHashedPassword(
            email=user_data.email,
            password_hash=password_hash
        )
    )
    return registered_user_data


@router.post("/login/")
async def auth_user_issue_jwt(
    response: Response,
    user: UserRead = Depends(valiadate_auth_user),
    session=Depends(get_session)
):

    id_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    await AuthService(session).update_token(
        user_id=user.id,
        token=refresh_token,
        token_type=TokenType.REFRESH
    )

    response.set_cookie(
        key="session_id",
        value=f"Bearer {id_token}",
        httponly=True,  # to prevent JavaScript access
        # secure=True,
    )




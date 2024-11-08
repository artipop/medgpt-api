from fastapi import APIRouter, Depends, Response, Request

from database import get_session

from common.logger import logger
from common.auth.utils import AuthType
from common.auth.schemas.user import UserRead
from common.auth.dependencies import preprocess_auth, authenticate
from native_auth.dependencies import logout as logout_native
from google_auth.dependencies import logout as logout_google


router = APIRouter(
    prefix="/common-auth",
    tags=["auhorization"]
)


@router.post("/logout/")
async def logout(
    request: Request, 
    response: Response,
    session=Depends(get_session)
):
    id_token, id_token_payload, auth_scheme = preprocess_auth(request=request)
    
    logger.warning(auth_scheme)

    if auth_scheme == AuthType.NATIVE:
        await logout_native(id_token_payload, session)
    
    elif auth_scheme == AuthType.GOOGLE:
        await logout_google(id_token_payload, session)

    response.delete_cookie(
        key="session_id", 
        httponly=True, 
        secure=True
    )

    #TODO(weldonfe): uncomment and change redirection route in row below 
    # return RedirectResponse(url="/google-auth/login")


@router.get("/users/me/")
async def auth_user_check_self_info(
    user: UserRead = Depends(authenticate)
):
    print(type(user))
    return user


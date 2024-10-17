import aiohttp
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from database import get_session
from settings import settings
from common.logger import logger
from google_auth.dependencies import state_storage
from google_auth.utils.id_token_validation import validate_id_token
from google_auth.utils.requests import (
    exchage_code_to_tokens,
    get_user_info_from_provider,
    get_new_access_token,
    revoke_token
)
from google_auth.dependencies import security_scheme
from google_auth.services.oidc_service import OIDCService

from pprint import pprint

router = APIRouter(
    prefix="/google-auth",
    tags=["google authorization"]
)

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
    request: Request,
    state: str=Depends(state_storage.validate),
    session=Depends(get_session)
):    
    access_token, refresh_token, id_token = await exchage_code_to_tokens(code)
    user_data_from_token_id = await validate_id_token(id_token, access_token)
    
    await OIDCService(session).get_or_create_user(
        user_data = user_data_from_token_id,
        access_token=access_token,
        refresh_token=refresh_token
    )

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


@router.get("/logout")
async def logout(
    response: Response, 
    token: str = Depends(security_scheme),
    session=Depends(get_session)
):
    """
    does not werify user identity
    revokes token from identity provider
    deletes access_token from cookies
    searches for corresponding refresh token in db and deletes both access and refresh
    """

    deleted_tokens = await OIDCService(session).logout(token)
    pprint(deleted_tokens)
    if deleted_tokens:
        for token in deleted_tokens:
            try:
                await revoke_token(token)
            except Exception as e: # token might be expired or allready revoked
                pass
    
    response.delete_cookie(key="Authorization", httponly=True, secure=True)
    
    #TODO(weldonfe): uncomment and change redirection route in row below 
    # return RedirectResponse(url="/google-auth/login")


@router.get("/refresh")
async def get_refresh_token(
    response: Response,
    access_token_to_refresh: str = Depends(security_scheme),
    session=Depends(get_session)
):
    refresh_token = await OIDCService(session).get_refresh_token(access_token_to_refresh)
    try: 
        reneved_access_token = await get_new_access_token(refresh_token)
    
    except Exception as e: # probably refresh token expired too
        await OIDCService(session).logout(access_token_to_refresh)
        response.delete_cookie(key="Authorization", httponly=True, secure=True)
        return
        # return RedirectResponse(url="/google-auth/login")

    await OIDCService(session).rotate_access_tokens(
        expired_token=access_token_to_refresh,
        renewed_token=reneved_access_token,
    )

    response.delete_cookie(key="Authorization", httponly=True, secure=True)
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {reneved_access_token}",
        httponly=True,  # to prevent JavaScript access
        secure=True,
    )
    return
    # return RedirectResponse(url="/docs")


@router.get("/get_current_user/")
async def get_current_user(
    token: str = Depends(security_scheme),
    session=Depends(get_session)
):
    is_token_not_expired = await OIDCService(session).is_token_not_expired_yet(token)
    if is_token_not_expired:
        print("ok")

    





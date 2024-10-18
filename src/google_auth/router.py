"""
This router implements authentication endpoints 
using the OpenID connect protocol, 
using Google as the identity provider

1. HOW TO AUTHENTICATE:
Use the endpoint <base_url>/google-auth/login to authenticate the user, 
In case of successful authentication:
    - a cookie of the form "Authorization: Bearer <access_token>" will be set
    - if this is a new user, a new record will be created in the database for him
otherwise "401 authenticated" will be returned

2. HOW TO LOGOUT:
Use endpoint <base_url>/google-auth/logout for authenticated user (cookie with access token must be transmitted)
all tokens for that user will be revoked from identity provider and backend DB

!!! Don't forget to change redirection url in router func to actual url for not authenticated users
(line should appear smth like: response = RedirectResponse(url=<actual app homepage>))

3. HOW TO REUSE DEPENDENCIES FOR BACKEND ROUTES PROTECTION
An example of proper usage is the route google_auth/try_auth in this route

There are 2 dependencies implemented in this router for these purposes:

1. authenticate func from google_auth.dependencies:
The main dependency that allows you to get user gmail from identity provider
that gmail can be used further to get any data from backend DB

This dependency completely controls the interaction with the identity provider and the token lifecycle, 
including updating access tokens, verifying the validity of the id token if necessary and managing cookies
so if it returned 401, then all user auth options have been exhausted and the user needs to be authenticated again

2. security_scheme var from google_auth.dependencies:
Checks for the access token, but does not validate something in any way. 

!!! It should be used only in service routes that serve the authentication process, 
do not use anywhere else besides them

"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import RedirectResponse

from database import get_session
from settings import settings
from common.logger import logger

from google_auth.dependencies import state_storage, authenticate, validate_id_token
from google_auth.utils.requests import exchage_code_to_tokens, revoke_token
from google_auth.dependencies import security_scheme
from google_auth.services.oidc_service import OIDCService
from google_auth.exceptions import OpenIDConnectException
from google_auth.schemas.oidc_user import OIDCUserRead
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
    try: 
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
    
    except HTTPException as e:
        logger.warning(e)
        raise OpenIDConnectException(detail="Not authenticated")


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
    if deleted_tokens:
        for token in deleted_tokens:
            try:
                await revoke_token(token)
            except Exception as e: # token might be expired or allready revoked
                pass
    
    response.delete_cookie(key="Authorization", httponly=True, secure=True)
    
    #TODO(weldonfe): uncomment and change redirection route in row below 
    # return RedirectResponse(url="/google-auth/login")


@router.get("/try_auth", response_model=OIDCUserRead)

async def get_refresh_token(
    oidc_user=Depends(authenticate),
    session=Depends(get_session)
):
    """
    endpoint to test auth, 
    when requested by authenticated user
    should return existing user info from provider with addition of primary key from db table oidc_users   
    """
    user_data = await OIDCService(session).get_user(user_data=oidc_user)
    return user_data




    





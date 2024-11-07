from fastapi import Request, Response, Depends
from common.auth.utils import (
    AuthType,
    get_auth_from_cookie,
    determine_auth_scheme,
    decode_jwt_without_verification
)
from common.logger import logger

from common.auth.exceptions import AuthException

from google_auth.dependencies import authenticate as authenticate_google
from native_auth.dependencies import authenticate as authenticate_native

from database import get_session


def preprocess_auth(request: Request):
    id_token = get_auth_from_cookie(request=request, cookie_name="session_id")
    id_token_payload = decode_jwt_without_verification(id_token)
    auth_scheme = determine_auth_scheme(id_token_payload)

    return id_token, id_token_payload, auth_scheme


async def authenticate(
        request: Request,
        response: Response,
        session=Depends(get_session) # TODO(weldonfe): determine type hint here, maybe posgresql.async_session or smth?...
    ):

    id_token, id_token_payload, auth_scheme = preprocess_auth(request=request)
    logger.critical(auth_scheme)
    try: 
        if auth_scheme == AuthType.GOOGLE:
            logger.critical("TRYING AUTH WITH GOOGLE")
            user = await authenticate_google(id_token, response, session)
            return user


        elif auth_scheme == AuthType.NATIVE:
            logger.critical("TRYING AUTH WITH NATIVE")
            user = await authenticate_native(id_token, response, session) 
            return user
    
    except Exception as e: # TODO(weldonfe): need to specify wich exceptions can be raised here
        logger.critical(e)
        raise AuthException(
            detail="Not authenticated"
        )    
    




from fastapi import Request, Depends
from common.auth.utils import (
    AuthScheme,
    get_auth_from_cookie,
    determine_auth_scheme,
    decode_jwt_without_verification
)
from common.auth.exceptions import AuthException

from google_auth.dependencies import authenticate as authenticate_google
from native_auth.dependencies import authenticate as authenticate_native

from database import get_session



def preprocess_auth(request: Request):
    id_token = get_auth_from_cookie(request, "session_id")
    id_token_payload = decode_jwt_without_verification(id_token)
    auth_scheme = determine_auth_scheme(id_token_payload)

    return id_token, id_token_payload, auth_scheme

def authenticate(
        request: Request,
        session=Depends(get_session) # TODO(weldonfe): determine type hint here, maybe posgresql.async_session or smth?...
    ):

    id_token, id_token_payload, auth_scheme = preprocess_auth(request=request)

    try: 
        if auth_scheme == AuthScheme.GOOGLE:
            user = authenticate_google(id_token, session)
        
        elif auth_scheme == AuthScheme.NATIVE:
            user = authenticate_native(id_token, session) 
    
    except Exception: # TODO(weldonfe): need to specify wich exceptions can be raised here
        raise AuthException(
            detail="Not authenticated"
        )    
    
    return user




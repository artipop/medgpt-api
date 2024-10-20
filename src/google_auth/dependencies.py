from fastapi import Response, Depends, HTTPException
from jose import jwt, JWTError
from typing import Dict

from settings import settings
from database import get_session
from common.logger import logger
from google_auth.services.oidc_service import OIDCService
from google_auth.exceptions import OpenIDConnectException
from google_auth.schemas.oidc_user import UserInfoFromIDProvider
from google_auth.utils.state_storage import StateStorage
from google_auth.utils.security_handler import OpenIDConnectHandler
from google_auth.utils.id_provider_certs import IdentityProviderCerts
from google_auth.utils.requests import (
    get_user_info_from_provider,
    get_new_tokens,
)
security_scheme = OpenIDConnectHandler(settings)
state_storage = StateStorage() # TODO(weldonfe): refactor somehow later, maybe to Redis storage?


async def authenticate(
    response: Response,
    session = Depends(get_session),
    token: str = Depends(security_scheme),
) -> UserInfoFromIDProvider:
    is_token_expired = await OIDCService(session).is_token_expired(token)
    # try:
    if is_token_expired:
        reneved_access_token = await refresh_token(session, token)
        token = reneved_access_token

        response.delete_cookie(key="Authorization", httponly=True, secure=True)
        response.set_cookie(
            key="Authorization",
            value=f"Bearer {reneved_access_token}",
            httponly=True,  # to prevent JavaScript access
            secure=True,
        )

    user_info = await get_user_info_from_provider(token=token)
    return UserInfoFromIDProvider(**user_info)

    # except HTTPException as e:
    #     response.delete_cookie(key="Authorization", httponly=True, secure=True)
    #     logger.warning(e)
    #     raise e
        # raise OpenIDConnectException(detail="Not authenticated")
    

async def refresh_token(
    session,
    access_token_to_refresh,
):
    refresh_token = await OIDCService(session).get_refresh_token(access_token_to_refresh)
    try: 
        reneved_access_token, reneved_id_token = await get_new_tokens(refresh_token)
        await validate_id_token(reneved_id_token, reneved_access_token) 
    
    except HTTPException as e: # probably refresh token expired too
        await OIDCService(session).logout(access_token_to_refresh)
        raise OpenIDConnectException(detail="Not authenticated")

    await OIDCService(session).rotate_access_tokens(
        expired_token=access_token_to_refresh,
        renewed_token=reneved_access_token,
    )

    return reneved_access_token


async def validate_id_token(id_token: str, access_token: str) -> UserInfoFromIDProvider:
    """
    if id token can't be successfuly decoded with access token and google client id,
    than id token is incorrect
    reference: https://developers.google.com/identity/openid-connect/openid-connect?hl=ru#validatinganidtoken
    """                
    def decode_id_token(id_token: str, access_token: str, cert: Dict):
        token_id_payload = jwt.decode(
            token=id_token,
            key=cert,
            audience=settings.google_client_id,
            issuer=settings.certs_issuer,
            access_token=access_token
        )
        # here we can check expiration date, audience and client id,
        # but documentation says that it's unnecessary in our case (reference in func desc)
        return UserInfoFromIDProvider(**token_id_payload)
    
    try:
        unverified_header = jwt.get_unverified_header(id_token)
        cert = await IdentityProviderCerts().find_relevant_cert(kid = unverified_header.get("kid", ""))
        user_data = decode_id_token(id_token, access_token, cert)
        
        logger.info("id token validation successful")
        
        return user_data
    
    except (HTTPException, JWTError) as e:
        logger.warinig(e)
        raise OpenIDConnectException(deatail="Id token validation failed")

    
        




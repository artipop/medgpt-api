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
from google_auth.utils.id_provider_certs import IdentityProviderCerts
from google_auth.utils.requests import (
    get_user_info_from_provider,
    get_new_tokens,
)

from jose import jwt, JWTError
from datetime import datetime, timezone

from google_auth.utils.requests import revoke_token
from common.auth.schemas.token import TokenType
from common.auth.services.auth_service import AuthService
from common.auth.exceptions import AuthException
from pprint import pprint

state_storage = StateStorage() # TODO(weldonfe): refactor somehow later, maybe to Redis storage?


async def authenticate(
    id_token: str, 
    response: Response, 
    session=Depends(get_session)
):
    email_from_unverified_payload  = jwt.get_unverified_claims(id_token).get("email", "")
    if is_id_token_expired(id_token):
        logger.critical("GOING TO RENEW OIDC TOKENS")
        access_token, id_token = await rotate_tokens(
            user_email=email_from_unverified_payload,
            session=session
        )

        response.set_cookie(
            key="session_id",
            value=f"Bearer {id_token}",
            httponly=True,  # to prevent JavaScript access
            secure=True,
        )
    
    else:
        access_token, refresh_token = await AuthService(session).get_oidc_tokens_by_mail(
        email=email_from_unverified_payload
    )


    try:
        user_data = await validate_id_token(id_token, access_token)
        return user_data

    except Exception as e: #specify exception or token exp validation here
        raise AuthException("Smth wrng with token!")



    # async def authenticate(
#     response: Response,
#     token: str,
#     session = Depends(get_session)
# ):
    # is_token_expired = await OIDCService(session).is_token_expired(token)
#     try:
#         if is_token_expired:
            # reneved_access_token = await refresh_token(session, token)
#             token = reneved_access_token
            
#             response.delete_cookie(key="Authorization", httponly=True, secure=True)
#             response.set_cookie(
#                 key="Authorization",
#                 value=f"Bearer {reneved_access_token}",
#                 httponly=True,  # to prevent JavaScript access
#                 secure=True,
#             )

#         user_info = await get_user_info_from_provider(token=token)
#         return UserInfoFromIDProvider(**user_info)

#     except HTTPException as e:
#         response.delete_cookie(key="Authorization", httponly=True, secure=True)
#         logger.warning(e)
#         raise OpenIDConnectException(detail="Not authenticated")
    

async def rotate_tokens(
        user_email: str, 
        session
    ):
    
    old_access_token, refresh_token = await AuthService(session).get_oidc_tokens_by_mail(
        email=user_email
    )

    renewed_access_token, renewed_id_token = await get_new_tokens(refresh_token)
    
    user = await AuthService(session).get_user_by_mail(email=user_email)
    logger.critical("HERERERERERERERERERERERERERE")
    await AuthService(session).update_token(
        user_id=user.id,
        token=renewed_access_token,
        token_type=TokenType.REFRESH.value
    )

    return renewed_access_token, renewed_id_token






def is_id_token_expired(token: str):
    payload = jwt.get_unverified_claims(token)
    token_expires_at = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
    logger.critical(token_expires_at)

    now = datetime.now(timezone.utc)

    logger.critical(f"NOW: {now}")
    logger.critical(f"EXPIRES AT {token_expires_at}")
    
    logger.warning((now - token_expires_at).total_seconds())
    if (now - token_expires_at).total_seconds() > 0:
        logger.critical("TOKEN EXPIRED")
        return True
    
    return False


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


async def validate_id_token(
        id_token: str, 
        access_token: str
    ) -> UserInfoFromIDProvider:
    """
    if id token can't be successfuly decoded with access token and google client id,
    than id token is incorrect
    reference: https://developers.google.com/identity/openid-connect/openid-connect?hl=ru#validatinganidtoken
    """
    # TODO(weldonfe): rewrite that code to jwt lib instead of jose
    def decode_id_token(
            id_token: str, 
            access_token: str, 
            cert: Dict):
        
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
        user_data = decode_id_token(
            id_token, 
            access_token, 
            cert
        )
        
        logger.info("id token validation successful")
        
        return user_data
    
    except (HTTPException, JWTError) as e:  
        logger.warning(e)
        raise OpenIDConnectException(detail="Id token validation failed")
    

async def logout(
        id_token_payload: Dict,
        session=Depends(get_session)
    ):
    deleted_tokens = await AuthService(session).logout_oidc_user(
        UserInfoFromIDProvider(
            email=id_token_payload.get("email", "")
        )
    )

    if deleted_tokens:
        for token_data in deleted_tokens:
            try:
                await revoke_token(token_data.token)
            except Exception as e: # token might be expired or allready revoked
                pass

    
        




import aiohttp
from typing import Optional, Dict, List
from fastapi import Depends
from jose import jwt

from settings import settings
from common.logger import logger
from google_auth.dependencies import security_scheme
from google_auth.utils.http_client import HttpClient
from google_auth.exceptions import OpenIDConnectException
from google_auth.schemas import UserFromProvider


async def get_user_info_from_provider(
    access_token: str = Depends(security_scheme)
) -> UserFromProvider:
    """   
    Requests user information from OpenID provider (Google auth server) 
    """
    http_session: aiohttp.ClientSession = await HttpClient().get_session()
    async with http_session.get(
        settings.google_userinfo_url,
        headers={"Authorization": f"Bearer {access_token}"}
    ) as user_info_resp:
        user_info = await user_info_resp.json()

    return UserFromProvider(**user_info)


async def exchage_code_to_tokens(
    code: str,
) -> Dict[str, str]:
    http_session: aiohttp.ClientSession = await HttpClient().get_session()
    exchange_request_payload = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.redirect_google_to_uri,
        "grant_type": "authorization_code",
    }
    async with http_session.post(
        url=settings.google_token_url, 
        data=exchange_request_payload
    ) as token_resp:
        if token_resp.status != 200:
            raise OpenIDConnectException(
                detail="Failed to exchange code for token"
            )
        
        response_data = await token_resp.json()
        return (
            response_data.get("access_token"),
            response_data.get("refresh_token"),
            response_data.get("id_token")
        )
    

async def validate_id_token(
    id_token: str, 
    access_token: str, 
):
    """
    if id token can't be successfuly decoded with access token and google client id,
    than id token is incorrect
    reference: https://developers.google.com/identity/openid-connect/openid-connect?hl=ru#validatinganidtoken
    """
    
    async def get_certs():
        """
        requests actual certs emitted by google
        """
        http_session: aiohttp.ClientSession = await HttpClient().get_session()
        async with http_session.get(url=settings.google_certs_url) as certs_resp:
            certs = await certs_resp.json()
            return certs

    def find_relevant_cert(id_token: str, certs: List[Dict]):
        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        
        for cert in certs.get("keys"):
            if cert.get("kid") == kid:
                return cert
                
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

    try: 
        certs = await get_certs()
        decode_id_token(
            id_token,
            access_token,
            cert=find_relevant_cert(id_token, certs)
        )

    except Exception as e: # TODO(weldonfe): clarify which exceptions can be raised here
        raise OpenIDConnectException(deatail="Id token validation failed")
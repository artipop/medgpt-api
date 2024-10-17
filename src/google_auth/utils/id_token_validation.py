from typing import Dict, List
from jose import jwt

from settings import settings
from common.logger import logger
from common.singleton import singleton
from google_auth.exceptions import OpenIDConnectException
from google_auth.utils.requests import get_certs
from pprint import pprint
from google_auth.schemas.oidc_user import UserInfoFromIDProvider


@singleton
class IdentityProviderCerts:
    """
    certs rotated on identity provider side at least every two weeks
    that class requests actual certs in two cases:
    - on app startup by lifespan event
    - during validate_id_token function call, when func cant find relevant cert in existing
    """
    def __init__(self):
        self.certs = None

    async def renew_certs(self):
        self.certs = await get_certs()

    async def get_certs(self):
        if not self.certs:
            self.certs = await self.renew_certs()
        return self.certs
    
    def find_cert_by_kid(self, kid: str):
        if not self.certs:
            return 
        
        for cert in self.certs.get("keys"):
            if cert.get("kid") == kid:
                return cert
        return
    
    async def find_relevant_cert(self, kid: str):
        cert = self.find_cert_by_kid(kid)
        if cert:
            return cert
        
        # func reached that line for one of two reasons
        # 1. certs are outdated
        # 2. kid is incorrect
        
        self.certs = await self.renew_certs()
        cert = self.find_cert_by_kid(kid)
        
        if not cert:
            raise OpenIDConnectException(deatail="Relevant identity provider cert not found")
        
        return cert 
     

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
    
    except Exception as e: # TODO(weldonfe): clarify which exceptions can be raised here
        raise OpenIDConnectException(deatail="Id token validation failed")
    

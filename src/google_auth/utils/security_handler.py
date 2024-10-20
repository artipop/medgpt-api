from enum import Enum, auto
from typing import Optional, Dict
from fastapi import Request, HTTPException

from google_auth.exceptions import OpenIDConnectException


class TransportMethod(Enum):
    headers = auto()
    cookies = auto()


class OpenIDConnectHandler:
    """
    Custom implementeation of OpenID connect auth scheme
    because OpenIdConnect class from fastapi.sequrity doesn't provide cookie based flow
    """
    def __init__(
        self, 
        settings: Dict,
        transport_method: TransportMethod = TransportMethod.cookies
    ):
        self.settings = settings
        self.transport_method = transport_method
        # self.http_client = get_http_client()
    
    def parse_auth_data(
        self, 
        request: Request,
    ) -> str:
        
        """
        Extracts token data from either headers or cookies. 
        Expects 'Authorization' header with 'Bearer' token or cookie with 'Authorization'.
        
        Returns:
            str: The token extracted from headers or cookies.
        
        Raises:
            OpenIDConnectException: If token is not provided or in the wrong format.
        """
        auth_data = (
            request.cookies 
            if self.transport_method == TransportMethod.cookies 
            else request.headers
        )
        auth_string = auth_data.get("Authorization")
        if not auth_string :
            raise OpenIDConnectException(detail="No token provided in auth data")

        auth_data = auth_string.split(" ")
        if len(auth_data) != 2 or auth_data[0] != "Bearer":
            raise OpenIDConnectException(detail="Invalid token format in auth data")

        token = auth_data[1]
        if not token:
            raise OpenIDConnectException(detail="No token provided in auth data")
             
        return token
    
    async def __call__(self, request: Request) -> Optional[str]:
        try: 
            return self.parse_auth_data(request=request)   
        except HTTPException as e:
            raise e



    

        



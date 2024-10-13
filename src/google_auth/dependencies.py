from typing import Set
from settings import settings
from google_auth.exceptions import StateTokenException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
import uuid
import aiohttp
from common.logger import logger

class StateStorage:
    def __init__(self):
        self.storage = set()

    def produce(self) -> str:
        state = str(uuid.uuid4())
        self.storage.add(state)

        jwt_token = jwt.encode(
            claims={"state": state}, 
            key=settings.jwt_signing_key, 
            algorithm=settings.jwt_encoding_algo
        )

        return jwt_token

    def validate(self, state: str):
        try:
            state_from_response = jwt.decode(
                token=state, 
                key=settings.jwt_signing_key, 
                algorithms=[settings.jwt_encoding_algo]
            ).get("state")
            
            if state_from_response not in self.storage:
                raise StateTokenException(detail="Incorrect state token provided")
            
            self.storage.pop()

        except jwt.JWTError:
            raise StateTokenException(detail="Couldn't decode state token")        
 

# TODO(weldonfe): rewrite_to_singletone
class HttpClient:
    def __init__(self):
        self.session = None
        self.counter = 0

    async def init_session(self):
        """Initialize the aiohttp ClientSession."""
        if self.session is None:
            self.counter += 1
            logger.info(f"http session instance created, counter: {self.counter}")
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close the aiohttp ClientSession."""
        if self.session:
            await self.session.close()
            logger.info(f"http session properly closed, counter {self.counter}")
            self.session = None

    async def get_session(self) -> aiohttp.ClientSession:
        if not self.session:
            await self.init_session()
        
        return self.session


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.google_authorization_url,
    tokenUrl=settings.google_token_url
)

state_storage = StateStorage() # TODO(weldonfe): refactor somehow later, maybe to Redis storage?
http_client = HttpClient()
def get_http_client() -> HttpClient:
    return http_client


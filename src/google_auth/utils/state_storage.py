from settings import settings
from common.auth.exceptions import AuthException

from jose import jwt
import uuid


class StateStorage:
    # TODO(weldonfe): rewrite_to_singleton
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
                raise AuthException(detail="Incorrect state token provided")
            
            self.storage.pop()

        except jwt.JWTError:
            raise AuthException(detail="Couldn't decode state token")

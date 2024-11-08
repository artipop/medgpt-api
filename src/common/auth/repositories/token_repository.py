from database import AbstractRepository

from common.auth.models.token import Token
from common.auth.schemas.token import TokenCreate


class TokenRepository(AbstractRepository):
    model = Token

    async def create_or_update(self, token_data: TokenCreate):
        existing_token_data = await self.get_by_filter(
            {
                "user_id": token_data.user_id,
                "token_type": token_data.token_type
            }
        )
        
        if existing_token_data:
            token: Token = existing_token_data[0]
            token.token = token_data.token 
        else:
            token = await self.create(token_data)
            self._session.add(token)


        


            


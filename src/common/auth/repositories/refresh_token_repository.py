from sqlalchemy import select, delete

from database import AbstractRepository
from common.auth.models.refresh_token import RefreshToken
from google_auth.schemas.oidc_user import UserInfoFromIDProvider, OIDCUserCreate

from common.auth.schemas.token import TokenCreate
from common.auth.models.refresh_token import RefreshToken

class RefreshTokenRepository(AbstractRepository):
    model = RefreshToken

    async def create_or_update(self, token_data: TokenCreate):
        existing_token_data = await self.get_by_filter({"user_id": token_data.user_id})
        
        if existing_token_data:
            token: RefreshToken = existing_token_data[0]
            token.token = token_data.token 
        else:
            token = await self.create(token_data)
            self._session.add(token)


        


            


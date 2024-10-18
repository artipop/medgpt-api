from database import AbstractRepository
from google_auth.models.oidc_models import (
    OIDCUser, 
    RefreshToken, 
    AccessToken, 
    RefreshToAccessTokenMapping
)

from google_auth.schemas.oidc_user import (
    UserInfoFromIDProvider, 
    OIDCUserCreate,
    OIDCUserRead
)

from sqlalchemy import select, delete


class OIDCRepository(AbstractRepository):
    model = OIDCUser

    async def get_existing_user(self, user_data: UserInfoFromIDProvider):
        existing_user = await self.get_by_filter({"email": user_data.email})
        if existing_user:
            return existing_user[0]
    
    async def get_or_create_user(self, user_data: UserInfoFromIDProvider):
        existing_user = await self.get_existing_user(user_data)
        if existing_user:
            return existing_user 

        created_user = await self.create(OIDCUserCreate(email=user_data.email))

        return created_user


class AccessTokenRepository(AbstractRepository):
    model = AccessToken

    async def get_by_value(self, token: str):
        token_data = await self.get_by_filter({"token": token})
        if token_data:
            return token_data[0].created_at

    async def delete_by_value(self, token: str):
        db_response = await self._session.execute(
            delete(self.model).where(self.model.token == token).returning(self.model)
        )
        result = db_response.scalars().one_or_none()
        if result:
            return result.id 


class RefreshTokenRepository(AbstractRepository):
    model = RefreshToken


class RefreshToAccessTokenMappingRepository(AbstractRepository):
    model = RefreshToAccessTokenMapping
    
    async def get_refresh_token_by_access_token(self, access_token: str):
        query = (
            select(self.model, AccessToken, RefreshToken)
            .join(AccessToken, AccessToken.id == self.model.access_token_id)
            .join(RefreshToken, RefreshToken.id == self.model.refresh_token_id)
            .where(AccessToken.token==access_token)
        )
        result = await self._session.execute(query)
        return result.mappings().one_or_none()




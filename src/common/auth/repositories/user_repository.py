from sqlalchemy import select, delete

from database import AbstractRepository
from common.auth.models.user import User
from google_auth.schemas.oidc_user import UserInfoFromIDProvider, OIDCUserCreate


class UserRepository(AbstractRepository):
    model = User

    async def get_existing_user_by_mail(self, user_data: UserInfoFromIDProvider):
        existing_user = await self.get_by_filter({"email": user_data.email})
        if existing_user:
            return existing_user[0]
    

    async def get_or_create_oidc_user(self, user_data: UserInfoFromIDProvider):
        existing_user = await self.get_existing_user_by_mail(user_data)
        if existing_user:
            return existing_user 

        created_user = await self.create(OIDCUserCreate(email=user_data.email))

        return created_user
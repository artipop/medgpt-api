from sqlalchemy import select, delete

from database import AbstractRepository
from common.auth.models.user import User
from common.auth.schemas.user import UserCreate 
from google_auth.schemas.oidc_user import UserInfoFromIDProvider
from native_auth.schemas.user import UserCreatePlainPassword
from common.auth.models.auth_credentials import AuthCredentials

class UserRepository(AbstractRepository):
    model = User

    async def get_existing_user_by_mail(self, email: str):
        existing_user = await self.get_by_filter({"email": email})
        if existing_user:
            return existing_user[0]
    

    async def get_or_create_oidc_user(self, user_data: UserInfoFromIDProvider):
        existing_user = await self.get_existing_user_by_mail(email=user_data.email)
        if existing_user:
            return existing_user 

        created_user = await self.create(UserCreate(email=user_data.email))

        return created_user
    
    async def get_native_user_with_creds_by_email(self, email: str):
        query = (
            select(self.model, AuthCredentials)
            .where(self.model.email == email)
            .join(self.model.auth_credentials)
        )

        result = await self._session.execute(query)
        return result.first() 
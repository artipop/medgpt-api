from datetime import datetime, timezone

from google_auth.schemas.oidc_user import UserInfoFromIDProvider
# from google_auth.schemas.oidc_user import OIDCUserRead, OIDCUserCreate

from google_auth.exceptions import DBException

from common.auth.repositories.user_repository import UserRepository
from common.auth.repositories.refresh_token_repository import RefreshTokenRepository
from common.auth.repositories.auth_credentials_repository import AuthCredentialsRepository
from common.auth.models.auth_credentials import AuthType

from common.auth.schemas.token import TokenFromIDProvider, TokenCreate, TokenRead
from common.auth.schemas.auth_credentials import AuthCredentialsCreate
from common.auth.schemas.user import UserRead


class AuthService:
    def __init__(self, session):
        self.session = session

    async def get_user_by_mail(self, user_data: UserInfoFromIDProvider):
        "a method for getting user data from the database using his gmail"
        user_db_ans = await UserRepository(self.session).get_existing_user_by_mail(user_data)
        return UserRead.model_validate(user_db_ans, from_attributes=True)
    
    async def get_or_create_oidc_user(
        self, 
        user_data: UserInfoFromIDProvider,
        token_data: TokenFromIDProvider
    ):
        user_db_answer = await UserRepository(self.session).get_or_create_oidc_user(
            user_data=user_data
        )

        auth_db_answer = await AuthCredentialsRepository(self.session).get_or_create(
            AuthCredentialsCreate(
                user_id=user_db_answer.id,
                auth_type=AuthType.GOOGLE.value
            )
        )
        
        token_db_answer = await RefreshTokenRepository(self.session).create_or_update(
            TokenCreate(
                user_id=user_db_answer.id,
                token=token_data.token
            )
        )

        await self.session.commit()
        
        
    async def logout_oidc_user(self, user_data: UserInfoFromIDProvider):
        user_db_answer = await self.get_user_by_mail(user_data=user_data)
        if not user_db_answer:
            return
            
        deleted_tokens_db_answer = await RefreshTokenRepository(self.session).delete_by_value(
            field_name="user_id", 
            value=user_db_answer.id
        )
        if not deleted_tokens_db_answer:
            return
        
        deleted_tokens = [
            TokenRead.model_validate(token, from_attributes=True)
            for token
            in deleted_tokens_db_answer
        ]  

        await self.session.commit()
        
        return deleted_tokens

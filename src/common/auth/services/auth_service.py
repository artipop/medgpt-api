from datetime import datetime, timezone
from typing import Union
from google_auth.schemas.oidc_user import UserInfoFromIDProvider
# from google_auth.schemas.oidc_user import OIDCUserRead, OIDCUserCreate

from google_auth.exceptions import DBException

from common.auth.repositories.user_repository import UserRepository
from common.auth.repositories.refresh_token_repository import RefreshTokenRepository
from common.auth.repositories.auth_credentials_repository import AuthCredentialsRepository
from common.auth.utils import AuthType

from common.auth.exceptions import AuthException
from common.auth.schemas.token import TokenFromIDProvider, TokenCreate, TokenRead
from common.auth.schemas.auth_credentials import AuthCredentialsCreate
from common.auth.schemas.user import UserCreate, UserRead

from native_auth.schemas.user import (
    UserCreatePlainPassword, 
    UserCreateHashedPassword, 
    UserLogin, 
    UserOut, 
    UserInDB,
    UserFromToken
)


class AuthService:
    def __init__(self, session):
        self.session = session

    async def get_user_by_mail(self, email: str):
        "a method for getting user data from the database using his gmail"
        user_db_ans = await UserRepository(self.session).get_existing_user_by_mail(
            email=email
        )
        if user_db_ans:
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
        user_db_answer = await self.get_user_by_mail(email=user_data.email)
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
    
    async def check_user_existence_on_native_register(
        self, 
        user_data: UserCreatePlainPassword
    ):
        existing_user = await self.get_user_by_mail(email=user_data.email)
        if existing_user:
            raise AuthException(detail="User with given email already exists")


    async def register_native_user(
        self,
        user_data: UserCreateHashedPassword
    ):
        user_db_answer = await UserRepository(self.session).create(UserCreate(email=user_data.email))

        auth_db_answer = await AuthCredentialsRepository(self.session).create(
            AuthCredentialsCreate(
                user_id=user_db_answer.id,
                auth_type=AuthType.NATIVE.value,
                password_hash=user_data.password_hash
            )
        )

        await self.session.commit()

        return UserOut.model_validate(user_db_answer)
    

    async def get_native_user_by_mail(
        self,
        user_data: UserCreatePlainPassword
    ):
        existing_user_db_ans = await UserRepository(self.session).get_native_user_with_creds_by_email(
            email=user_data.email
        )
        if not existing_user_db_ans:
            raise AuthException(detail="No such user in DB")

        existing_user = UserInDB(
            id=existing_user_db_ans[0].id,
            email=existing_user_db_ans[0].email,
            created_at=existing_user_db_ans[0].created_at,
            is_verified=existing_user_db_ans[0].is_verified,
            password_hash=existing_user_db_ans[1].password_hash
        )

        return existing_user
    

    async def update_refresh_token(
        self,
        user_id: str,
        token: str
    ): 
        token_db_answer = await RefreshTokenRepository(self.session).create_or_update(
            TokenCreate(
                user_id=user_id,
                token=token
            )
        )
        await self.session.commit()

    
    async def get_user_by_id(self, user_id: str):
        user_db_answer = await UserRepository(self.session).get_by_id(user_id)
        return UserOut.model_validate(user_db_answer)
    

    async def get_refresh_token_by_user_id(self, user_id: str):
        token_db_answer = await RefreshTokenRepository(self.session).get_by_filter(
            {
                "user_id": user_id
            }
        )
        if token_db_answer:
            return token_db_answer[0].token
        

    async def delete_token_by_value(self, token: str):
        deleted_tokens_db_answer = await RefreshTokenRepository(self.session).delete_by_value(
            field_name="token", 
            value=token
        )
        await self.session.commit()




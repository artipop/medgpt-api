from datetime import datetime, timezone

from google_auth.models.oidc_repositories import (
    OIDCRepository, 
    RefreshTokenRepository, 
    AccessTokenRepository, 
    RefreshToAccessTokenMappingRepository
)
from google_auth.models.oidc_models import (
    AccessToken,
    RefreshToken,
)

from google_auth.schemas.oidc_user import UserInfoFromIDProvider
from google_auth.schemas.oidc_user import OIDCUserRead, OIDCUserCreate
from google_auth.schemas.token import TokenRead, TokenCreate, TokensRelationship
from google_auth.exceptions import DBException


class OIDCService:
    def __init__(self, session):
        self.session = session

    async def get_user(self, user_data: UserInfoFromIDProvider):
        "a method for getting user data from the database using his gmail"
        user_db_ans = await OIDCRepository(self.session).get_existing_user(user_data)
        return OIDCUserRead.model_validate(user_db_ans, from_attributes=True)

    async def get_or_create_user(
        self, 
        user_data: UserInfoFromIDProvider,
        access_token: str,
        refresh_token: str, 
    ):
        """
        Method for creating or updating user data after authentication
        """
        try: 
            user_db_ans = await OIDCRepository(self.session).get_or_create_user(user_data)            
            access_token_db_ans = await AccessTokenRepository(self.session).create(
                TokenCreate(
                    user_id=user_db_ans.id,
                    token=access_token
                )
            )
            refresh_token_db_ans = await RefreshTokenRepository(self.session).create(
                TokenCreate(
                    user_id=user_db_ans.id,
                    token=refresh_token
                )
            )
            relation = await RefreshToAccessTokenMappingRepository(self.session).create(
                TokensRelationship(
                    access_token_id=access_token_db_ans.id,
                    refresh_token_id=refresh_token_db_ans.id
                )
            )
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise DBException(detail="Smth wrong with DB")
        
    async def logout(self, access_token: str):
        try: 
            tokens_relationship = await (
                RefreshToAccessTokenMappingRepository(self.session).get_refresh_token_by_access_token(
                    access_token=access_token
                )
            )
            if not tokens_relationship:
                return
            
            await AccessTokenRepository(self.session).delete_by_id(
                tokens_relationship[AccessToken].id
            )
            await RefreshTokenRepository(self.session).delete_by_id(
                tokens_relationship[RefreshToken].id
            )
            deleted_access_token = tokens_relationship[AccessToken].token
            deleted_refresh_token = tokens_relationship[RefreshToken].token

            await self.session.commit()

            return deleted_access_token, deleted_refresh_token
        
        except Exception as e:
            await self.session.rollback()
            raise DBException(detail="Smth wrong with DB")
    

    async def get_refresh_token(self, access_token: str):
        try: 
            tokens_relationship = await (
                RefreshToAccessTokenMappingRepository(self.session).get_refresh_token_by_access_token(
                    access_token=access_token
                )
            )
            if tokens_relationship:
                return tokens_relationship[RefreshToken].token
        
        except Exception as e:
            await self.session.rollback()
            raise DBException(detail="Smth wrong with DB")

        

    async def rotate_access_tokens(
            self, 
            expired_token: str,
            renewed_token: str,
        ):
        try: 
            tokens_relationship = await (
                RefreshToAccessTokenMappingRepository(self.session).get_refresh_token_by_access_token(
                    access_token=expired_token
                )
            )
            if not tokens_relationship:
                return
            
            await AccessTokenRepository(self.session).delete_by_id(
                tokens_relationship[AccessToken].id
            )
            # creating new access_token record
            access_token_db_ans = await AccessTokenRepository(self.session).create(
                TokenCreate(
                    user_id=tokens_relationship[AccessToken].user_id,
                    token=renewed_token
                )
            )


            # setting new access to refresh token relationship record
            relation = await RefreshToAccessTokenMappingRepository(self.session).create(
                TokensRelationship(
                    access_token_id=access_token_db_ans.id,
                    refresh_token_id=tokens_relationship[RefreshToken].id
                )
            )
            # deleting expired access token and relationship record with it

            await AccessTokenRepository(self.session).delete_by_id(
                tokens_relationship[AccessToken].id
            )
            await self.session.commit()
        
        except Exception as e:
            self.session.rollback()
            raise DBException(detail="Smth wrong with DB")


    async def is_token_expired(self, access_token: str):
        expiration_timestamp = await AccessTokenRepository(self.session).get_by_value(access_token)
        if not expiration_timestamp: # token already deleted from db
            return True
        
        expiration_timestamp = expiration_timestamp.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        
        TOKEN_EXPIRES_IN = 3600 * 0.95
        # TOKEN_EXPIRES_IN_FOR_DEBUG = 2
        if (now - expiration_timestamp).total_seconds() < TOKEN_EXPIRES_IN:
        # if (now - expiration_timestamp).total_seconds() < TOKEN_EXPIRES_IN_FOR_DEBUG:
            return False
        return True
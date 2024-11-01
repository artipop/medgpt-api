from datetime import datetime, timezone
from users.repositories.native_user_repository import NativeUserRepository
from users.schemas.naitve_user_schemas import (
    UserCreatePlainPassword, 
    UserCreateHashedPassword, 
    UserLogin, 
    UserOut, 
    UserInDB,
    UserFromToken
)

from native_auth.exceptions import NativeAuthException

class NativeUserService:
    def __init__(self, session):
        self.session = session

    async def check_user_existence_on_register(self, user_data: UserCreatePlainPassword):
        if existing_user := await NativeUserRepository(self.session).check_user_existence(user_data):
            raise NativeAuthException(
                detail="User with provided username or email address already exists"
            )
        
    async def create_user(self, user_data: UserCreateHashedPassword):
        created_user = await NativeUserRepository(self.session).create(user_data)
        await self.session.commit()
        return UserOut.model_validate(created_user)
    
    async def get_user_by_email(self, user_data: UserLogin):
        existing_user = await NativeUserRepository(self.session).get_one_or_none_by_filter(
            {"email": user_data.email}
        )
        if not existing_user:
            raise NativeAuthException(
                detail="No such user in DB"
            )
        
        return UserInDB.model_validate(existing_user)
    
    async def get_user_by_id(self, user_data: UserFromToken):
        existing_user = await NativeUserRepository(self.session).get_by_id(id=user_data.id)
        if not existing_user:
            raise NativeAuthException(
                detail="No such user in DB"
            )
        
        return UserOut.model_validate(existing_user)



        
        

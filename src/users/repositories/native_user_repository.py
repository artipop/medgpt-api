from database import AbstractRepository
from sqlalchemy import select, delete
from users.models.native_user import NativeUser
from users.schemas.naitve_user_schemas import (
    UserCreatePlainPassword, 
    UserCreateHashedPassword, 
    UserLogin, 
    UserOut, 
    UserInDB
)


class NativeUserRepository(AbstractRepository):
    model = NativeUser

    async def get_one_or_none_by_filter(self, kwargs):
        query = select(self.model).filter_by(**kwargs)
        result = await self._session.execute(query)
        return result.scalars().one_or_none()
    
    async def check_user_existence(self, user_data: UserCreatePlainPassword):
        query = select(self.model).filter(
            (self.model.username == user_data.username) | (self.model.email == user_data.email)
        )
        result = await self._session.execute(query)
        return result.scalars().one_or_none()






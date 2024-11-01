import uuid
from sqlalchemy import ForeignKey, String, UUID, TIMESTAMP, Boolean, LargeBinary, func
from sqlalchemy.orm import relationship
from datetime import datetime

from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Base, AbstractRepository
from users.schemas.naitve_user_schemas import (
    UserCreatePlainPassword, 
    UserCreateHashedPassword, 
    UserLogin, 
    UserOut, 
    UserInDB
)

# class User(Base):
#     __tablename__ = 'users'
#     id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
#     email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
#     
#     created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
#     
#     refresh_tokens = relationship("RefreshTokens", back_populates="user")

class NativeUser(Base):
    __tablename__ = 'native_users'
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())




# class UserRepository(AbstractRepository):
#     model =  User
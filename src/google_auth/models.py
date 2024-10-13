import uuid
from sqlalchemy import ForeignKey, String, UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime

from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Base, AbstractRepository


class User(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    # email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # name: Mapped[str] = mapped_column(String(255))
    google_id: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    refresh_tokens = relationship("RefreshTokens", back_populates="user")


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    user = relationship("Users", back_populates="refresh_tokens")



class UserRepository(AbstractRepository):
    model =  User
import uuid
from sqlalchemy import ForeignKey, String, UUID, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from pydantic import EmailStr

from database import Base


class OIDCUser(Base):
    __tablename__ = 'oidc_users'
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    email: Mapped[EmailStr] = mapped_column(String(255), unique=True, nullable=False)
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    access_tokens = relationship("AccessToken", back_populates="user")


class BaseToken(Base):
    __abstract__ = True  # This class will not create a table
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('oidc_users.id', ondelete='CASCADE'), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())


class AccessToken(BaseToken):
    __tablename__ = 'access_tokens'
    
    user = relationship("OIDCUser", back_populates="access_tokens")


class RefreshToken(BaseToken):
    __tablename__ = 'refresh_tokens'
    
    user = relationship("OIDCUser", back_populates="refresh_tokens")


class RefreshToAccessTokenMapping(Base):
    __tablename__ = 'refresh_tokens_access_tokens'
    
    refresh_token_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('refresh_tokens.id', ondelete='CASCADE'), primary_key=True)
    access_token_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('access_tokens.id', ondelete='CASCADE'), primary_key=True)



















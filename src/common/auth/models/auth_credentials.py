import uuid
from datetime import datetime
from sqlalchemy import (
    Column, TIMESTAMP, func, ForeignKey, UniqueConstraint, Enum, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from pydantic import EmailStr
from enum import Enum as PyEnum

from database import Base


class AuthCredentials(Base):
    __tablename__ = 'auth_credentials'
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.id'), nullable=False)
    auth_type: Mapped[str] = mapped_column(nullable=False)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="auth_credentials")

    __table_args__ = (
        UniqueConstraint('auth_type', 'user_id', name='uq_auth_type_user'),
    )
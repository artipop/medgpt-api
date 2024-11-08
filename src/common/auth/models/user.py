import uuid
from sqlalchemy import Boolean, ForeignKey, String, UUID, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from pydantic import EmailStr

from database import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    email: Mapped[EmailStr] = mapped_column(String(255), unique=True, nullable=False)
    # TODO(weldonde): change is_verified default value to False when finish testing
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    
    tokens = relationship("Token", back_populates="user")
    auth_credentials = relationship("AuthCredentials", back_populates="user")
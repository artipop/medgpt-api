import uuid
from sqlalchemy import (
    Float,
    ForeignKey,
    String,
    UUID
)

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, DECIMAL, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

from database import Base, AbstractRepository


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)


class UserRepository(AbstractRepository):
    model =  User
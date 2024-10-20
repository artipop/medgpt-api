import uuid
from sqlalchemy import ForeignKey, String, UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime

from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Base, AbstractRepository


# class User(Base):
#     __tablename__ = 'users'
#     id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
#     email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

#     refresh_tokens = relationship("RefreshTokens", back_populates="user")






# class UserRepository(AbstractRepository):
#     model =  User
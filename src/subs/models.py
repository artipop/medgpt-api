import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, UUID, TIMESTAMP
from sqlalchemy.orm import relationship, mapped_column, Mapped

from database import Base


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(String(100))
    expiration_date: Mapped[datetime] = mapped_column(TIMESTAMP)
    provider: Mapped[str] = mapped_column(String(100), nullable=True)  # ?

    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.id'))
    user = relationship('User', back_populates='subscription')

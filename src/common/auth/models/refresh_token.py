import uuid
from sqlalchemy import ForeignKey, String, UUID, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from database import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.id'), nullable=False)
    token: Mapped[String] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")
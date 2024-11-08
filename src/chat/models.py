import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, Text, UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped

from database import Base


class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    owner_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.id'))

    owner = relationship('User', back_populates='chats')
    messages = relationship('Message', back_populates='chat', cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    content = mapped_column(Text, nullable=False)
    chat_id = mapped_column(UUID, ForeignKey('chats.id'))

    chat = relationship('Chat', back_populates='messages')
    references = relationship('LiteratureReference', back_populates='message', cascade="all, delete-orphan")


class LiteratureReference(Base):
    __tablename__ = 'literature_references'

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    message_id = Column(UUID, ForeignKey('messages.id'))

    message = relationship('Message', back_populates='references')

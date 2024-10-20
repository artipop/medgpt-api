from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from chat.models import Chat, Message
from database import AbstractRepository


class ChatRepository(AbstractRepository):
    model = Chat

    async def create(self, obj):
        self._session.add(obj)
        await self._session.commit()
        await self._session.refresh(obj)

    async def update(self, obj):
        self._session.add(obj)
        await self._session.commit()
        await self._session.refresh(obj)

    async def find_by_id(self, chat_id: UUID) -> Chat | None:
        sel = (select(Chat).where(Chat.id == chat_id).options(joinedload(Chat.messages)))
        result = await self._session.execute(sel)
        return result.scalars().first()


class MessageRepository(AbstractRepository):
    model = Message

    async def create(self, obj):
        self._session.add(obj)
        await self._session.commit()
        await self._session.refresh(obj)

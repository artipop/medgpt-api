from abc import ABC

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, insert
from sqlalchemy.exc import SQLAlchemyError

from settings import settings


meta = sqlalchemy.MetaData()

engine = create_async_engine(settings.db_url, echo=True)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base for all models."""
    metadata = meta


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session


class AbstractRepository(ABC):
    def __init__(self, session: AsyncSession):
        self._session = session

    model = None


    async def commit(self):
        try:
            await self._session.commit()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise e

    def rollback(self):
        self._session.rollback()

    async def get_by_id(self, id):
        return await self._session.get(self.model, id)

    async def get_all(self):
        result = await self._session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, obj):
        query = insert(self.model).values(**obj.model_dump()).returning(self.model)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def update_one(self, id, obj):
        query = update(self.model).where(self.model.id == id).values(**obj.model_dump()).returning(self.model)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def delete_by_id(self, id):
        result = await self._session.execute(delete(self.model).where(self.model.id == id))
        await self._session.commit()
        return result.rowcount

    async def get_by_filter(self, kwargs):
        query = select(self.model).filter_by(**kwargs)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def delete_by_value(self, field_name, value):
        field = getattr(self.model, field_name)
        stmt = delete(self.model).where(field == value).returning(self.model)
        result = await self._session.execute(stmt)

        return result.scalars().all()

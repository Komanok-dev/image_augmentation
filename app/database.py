from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from typing_extensions import Annotated

from app.settings import database_settings

async_engine: AsyncEngine = create_async_engine(
    database_settings.async_url, echo=True
)
sync_engine = create_engine(database_settings.sync_url, echo=True)


def get_async_sessionmaker():
    return sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


def get_sync_sessionmaker():
    return sessionmaker(
        bind=sync_engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async_sessionmaker = get_async_sessionmaker()
sync_sessionmaker = get_sync_sessionmaker()


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_sessionmaker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        else:
            await session.commit()
        finally:
            await session.close()


DatabaseSession = Annotated[AsyncSession, Depends(get_session)]

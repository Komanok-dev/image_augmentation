from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from app.database import (
    get_async_sessionmaker,
    get_session,
    get_sync_sessionmaker,
)

# ========================= Test sessionmaker =======================


def test_get_async_sessionmaker():
    async_sessionmaker = get_async_sessionmaker()
    assert isinstance(async_sessionmaker, sessionmaker)
    session = async_sessionmaker()
    assert isinstance(session, AsyncSession)


def test_get_sync_sessionmaker():
    sync_sessionmaker = get_sync_sessionmaker()
    assert isinstance(sync_sessionmaker, sessionmaker)
    session = sync_sessionmaker()
    assert isinstance(session, Session)


# ========================== Test get_session ========================


@pytest.mark.asyncio
async def test_get_session(mock_async_db_session):
    with patch("app.database.async_sessionmaker") as mock_sessionmaker:
        mock_sessionmaker.return_value.__aenter__.return_value = (
            mock_async_db_session
        )
        session_gen = get_session()
        session = await anext(session_gen)
        assert session is mock_async_db_session
        try:
            await session_gen.athrow(ValueError("Simulated error"))
        except ValueError:
            pass
        mock_async_db_session.commit.assert_not_called()
        mock_async_db_session.rollback.assert_called()
        mock_async_db_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_session_commit(mock_async_db_session):
    with patch("app.database.async_sessionmaker") as mock_sessionmaker:
        mock_sessionmaker.return_value.__aenter__.return_value = (
            mock_async_db_session
        )
        session_gen = get_session()
        session = await anext(session_gen)
        assert session is mock_async_db_session
        try:
            await session_gen.asend(None)
        except StopAsyncIteration:
            pass
        mock_async_db_session.commit.assert_awaited_once()
        mock_async_db_session.rollback.assert_not_called()
        mock_async_db_session.close.assert_awaited_once()

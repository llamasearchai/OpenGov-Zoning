"""Database session management utilities."""

from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .base import get_database_manager


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session for dependency injection."""
    db_manager = get_database_manager()
    async for session in db_manager.get_async_session():
        yield session


def get_sync_session() -> Generator[Session, None, None]:
    """Get sync database session for compatibility."""
    db_manager = get_database_manager()
    for session in db_manager.get_sync_session():
        yield session
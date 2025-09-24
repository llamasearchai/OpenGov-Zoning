"""Database base configuration and session management."""

import asyncio
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from ...core.config import get_settings
from ...core.exceptions.database import DatabaseConnectionError

Base = declarative_base()


class DatabaseManager:
    """Production-ready database manager with async support."""

    def __init__(self):
        """Initialize database manager with settings."""
        self.settings = get_settings()
        self._engine = None
        self._async_session_factory = None
        self._sync_session_factory = None

    @property
    def engine(self):
        """Get SQLAlchemy engine."""
        if self._engine is None:
            self._create_engine()
        return self._engine

    @property
    def async_session_factory(self):
        """Get async session factory."""
        if self._async_session_factory is None:
            self._create_async_session_factory()
        return self._async_session_factory

    @property
    def sync_session_factory(self):
        """Get sync session factory."""
        if self._sync_session_factory is None:
            self._create_sync_session_factory()
        return self._sync_session_factory

    def _create_engine(self):
        """Create SQLAlchemy engine with proper configuration."""
        try:
            # Parse database URL
            database_url = self.settings.database_url

            # Configure connection arguments based on database type
            connect_args = {}
            poolclass = None

            if database_url.startswith("sqlite"):
                # SQLite configuration
                connect_args = {
                    "check_same_thread": False,  # Allow multi-threading
                }
                poolclass = StaticPool  # Use StaticPool for SQLite in memory/testing
            elif database_url.startswith("postgresql"):
                # PostgreSQL configuration
                connect_args = {}

            # Create engine with production-ready settings
            self._engine = create_async_engine(
                database_url,
                # Connection pool settings
                pool_size=self.settings.db_pool_size,
                max_overflow=self.settings.db_max_overflow,
                pool_timeout=self.settings.db_pool_timeout,
                pool_recycle=self.settings.db_pool_recycle,
                pool_pre_ping=True,  # Verify connections before use
                pool_reset_on_return="commit",  # Reset connections on return
                # Performance settings
                echo=self.settings.debug,
                future=True,  # Use SQLAlchemy 2.0 style
                # Connection arguments
                connect_args=connect_args,
                poolclass=poolclass,
            )

        except Exception as e:
            raise DatabaseConnectionError(
                message=f"Failed to create database engine: {str(e)}",
                details={"database_url": database_url}
            )

    def _create_async_session_factory(self):
        """Create async session factory."""
        if self._engine is None:
            self._create_engine()

        self._async_session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autoflush=False,  # Don't autoflush on query
        )

    def _create_sync_session_factory(self):
        """Create sync session factory for compatibility."""
        if self._engine is None:
            self._create_engine()

        self._sync_session_factory = sessionmaker(
            bind=self._engine.sync_engine,
            expire_on_commit=False,
            autoflush=False,
        )

    async def create_all_tables(self):
        """Create all database tables."""
        if self._engine is None:
            self._create_engine()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all_tables(self):
        """Drop all database tables."""
        if self._engine is None:
            self._create_engine()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        if self._async_session_factory is None:
            self._create_async_session_factory()

        async with self._async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def get_sync_session(self) -> Generator:
        """Get sync database session for compatibility."""
        if self._sync_session_factory is None:
            self._create_sync_session_factory()

        session = self._sync_session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def health_check(self) -> dict:
        """Perform database health check."""
        try:
            async with self.get_async_session() as session:
                await session.execute(text("SELECT 1"))
                return {
                    "status": "healthy",
                    "database_url": self.settings.database_url.split("://")[0] + "://***",
                    "pool_size": self.settings.db_pool_size,
                    "max_overflow": self.settings.db_max_overflow,
                }
        except Exception as e:
            raise DatabaseConnectionError(
                message=f"Database health check failed: {str(e)}",
                details={"error": str(e)}
            )

    async def dispose(self):
        """Dispose of database connections."""
        if self._engine:
            await self._engine.dispose()


# Global database manager instance
_database_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get async database session."""
    db_manager = get_database_manager()
    async for session in db_manager.get_async_session():
        yield session


def get_sync_session() -> Generator:
    """Get sync database session for compatibility."""
    db_manager = get_database_manager()
    for session in db_manager.get_sync_session():
        yield session
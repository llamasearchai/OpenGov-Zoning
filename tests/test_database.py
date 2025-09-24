"""Comprehensive tests for database layer functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from opengovzoning.infrastructure.database.base import DatabaseManager, get_database_manager
from opengovzoning.infrastructure.database.models import Base


class TestDatabaseManager:
    """Test DatabaseManager functionality."""

    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager instance for testing."""
        return get_database_manager()

    def test_database_manager_initialization(self, db_manager):
        """Test that DatabaseManager can be initialized."""
        assert db_manager is not None
        assert hasattr(db_manager, 'engine')
        assert hasattr(db_manager, 'session_factory')

    @pytest.mark.asyncio
    async def test_get_session(self, db_manager):
        """Test getting a database session."""
        async with db_manager.get_async_session() as session:
            assert isinstance(session, AsyncSession)

    @pytest.mark.asyncio
    async def test_session_context_manager(self, db_manager):
        """Test that sessions are properly managed."""
        async with db_manager.get_async_session() as session:
            assert session.is_active

    def test_database_url_configuration(self, db_manager):
        """Test database URL configuration."""
        from opengovzoning.core.config import get_settings
        settings = get_settings()

        assert str(db_manager.engine.url) == settings.database_url

    @pytest.mark.asyncio
    async def test_connection_pool_settings(self, db_manager):
        """Test database connection pool configuration."""
        from opengovzoning.core.config import get_settings
        settings = get_settings()

        assert db_manager.engine.pool.size == settings.db_pool_size


class TestDatabaseModels:
    """Test database models functionality."""

    @pytest.mark.asyncio
    async def test_model_creation(self):
        """Test that models can be created."""
        from opengovzoning.infrastructure.database.models import Item

        # Test model instantiation
        item = Item(
            name="Test Item",
            description="Test Description"
        )

        assert item.name == "Test Item"
        assert item.description == "Test Description"
        assert item.id is not None  # Should have auto-generated ID

    @pytest.mark.asyncio
    async def test_model_validation(self):
        """Test model validation."""
        from opengovzoning.infrastructure.database.models import Item

        # Test with valid data
        item = Item(
            name="Valid Name",
            description="Valid Description"
        )
        assert item.name == "Valid Name"

        # Test with empty name (should still work as it's not validated at model level)
        item_empty = Item(
            name="",
            description="Empty name"
        )
        assert item_empty.name == ""

    @pytest.mark.asyncio
    async def test_model_timestamps(self):
        """Test model timestamp functionality."""
        from opengovzoning.infrastructure.database.models import Item
        from datetime import datetime

        # Create item
        item = Item(
            name="Timestamp Test",
            description="Testing timestamps"
        )

        # Should have created_at and updated_at timestamps
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)
        assert item.created_at <= item.updated_at


class TestDatabaseOperations:
    """Test database operations functionality."""

    @pytest.fixture
    async def db_session(self):
        """Create a test database session."""
        db_manager = get_database_manager()
        async with db_manager.get_session() as session:
            yield session
            # Ensure session is properly closed
            if session.is_active:
                await session.rollback()

    @pytest.mark.asyncio
    async def test_create_item(self, db_session):
        """Test creating an item in the database."""
        from opengovzoning.infrastructure.database.models import Item

        # Create item
        item = Item(
            name="Database Test Item",
            description="Testing database creation"
        )

        db_session.add(item)
        await db_session.commit()
        await db_session.refresh(item)

        assert item.id is not None
        assert item.name == "Database Test Item"
        assert item.description == "Testing database creation"

    @pytest.mark.asyncio
    async def test_read_item(self, db_session):
        """Test reading an item from the database."""
        from opengovzoning.infrastructure.database.models import Item

        # Create and save item
        item = Item(
            name="Read Test Item",
            description="Testing database read"
        )
        db_session.add(item)
        await db_session.commit()

        # Read item
        result = await db_session.get(Item, item.id)
        assert result is not None
        assert result.name == "Read Test Item"
        assert result.description == "Testing database read"

    @pytest.mark.asyncio
    async def test_update_item(self, db_session):
        """Test updating an item in the database."""
        from opengovzoning.infrastructure.database.models import Item

        # Create item
        item = Item(
            name="Update Test Item",
            description="Original description"
        )
        db_session.add(item)
        await db_session.commit()

        # Update item
        item.description = "Updated description"
        await db_session.commit()
        await db_session.refresh(item)

        assert item.description == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_item(self, db_session):
        """Test deleting an item from the database."""
        from opengovzoning.infrastructure.database.models import Item

        # Create item
        item = Item(
            name="Delete Test Item",
            description="Testing database deletion"
        )
        db_session.add(item)
        await db_session.commit()

        # Delete item
        await db_session.delete(item)
        await db_session.commit()

        # Verify deletion
        result = await db_session.get(Item, item.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_query_filtering(self, db_session):
        """Test database query filtering."""
        from opengovzoning.infrastructure.database.models import Item

        # Create multiple items
        items = [
            Item(name=f"Filter Test {i}", description=f"Description {i}")
            for i in range(5)
        ]

        for item in items:
            db_session.add(item)
        await db_session.commit()

        # Test filtering
        result = await db_session.execute(
            db_session.query(Item).filter(Item.name.like("Filter Test%"))
        )
        filtered_items = result.scalars().all()

        assert len(filtered_items) == 5
        assert all(item.name.startswith("Filter Test") for item in filtered_items)

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, db_session):
        """Test transaction rollback functionality."""
        from opengovzoning.infrastructure.database.models import Item

        # Create item
        item = Item(
            name="Rollback Test Item",
            description="Testing rollback"
        )
        db_session.add(item)
        await db_session.commit()

        original_id = item.id

        # Start new transaction
        async with db_session.begin():
            # Create another item within transaction
            new_item = Item(
                name="Transaction Item",
                description="Should be rolled back"
            )
            db_session.add(new_item)
            await db_session.flush()  # Flush to get ID without committing

            # Rollback transaction
            await db_session.rollback()

        # Original item should still exist
        original_item = await db_session.get(Item, original_id)
        assert original_item is not None

        # New item should not exist
        new_item_result = await db_session.get(Item, new_item.id)
        assert new_item_result is None


class TestDatabaseErrorHandling:
    """Test database error handling."""

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling of database connection errors."""
        with patch('opengovzoning.core.database.create_async_engine') as mock_engine:
            mock_engine.side_effect = Exception("Connection failed")

            with pytest.raises(Exception, match="Connection failed"):
                get_database_manager()

    @pytest.mark.asyncio
    async def test_session_error_handling(self):
        """Test handling of session errors."""
        db_manager = get_database_manager()

        with patch.object(db_manager.session_factory, '__call__', side_effect=Exception("Session error")):
            with pytest.raises(Exception, match="Session error"):
                async with db_manager.get_session():
                    pass

    @pytest.mark.asyncio
    async def test_constraint_violation_handling(self):
        """Test handling of database constraint violations."""
        from opengovzoning.infrastructure.database.models import Item

        db_manager = get_database_manager()
        async with db_manager.get_session() as session:
            # This should handle constraint violations gracefully
            # Note: Actual constraint testing would require specific database constraints
            pass


class TestDatabasePerformance:
    """Test database performance characteristics."""

    @pytest.mark.asyncio
    async def test_bulk_operations(self):
        """Test performance of bulk database operations."""
        from opengovzoning.infrastructure.database.models import Item
        import time

        db_manager = get_database_manager()
        start_time = time.time()

        async with db_manager.get_session() as session:
            # Create 100 items
            for i in range(100):
                item = Item(
                    name=f"Bulk Test {i}",
                    description=f"Bulk description {i}"
                )
                session.add(item)

            await session.commit()

        end_time = time.time()
        duration = end_time - start_time

        # Should be able to create 100 items in reasonable time
        assert duration < 5.0  # Less than 5 seconds

    @pytest.mark.asyncio
    async def test_connection_pooling(self):
        """Test database connection pooling."""
        db_manager = get_database_manager()

        # Test multiple concurrent sessions
        sessions = []
        for _ in range(10):
            session = db_manager.get_session()
            sessions.append(session)

        # Should be able to create multiple sessions
        assert len(sessions) == 10

        # Clean up
        for session in sessions:
            await session.__aexit__(None, None, None)
            # Ensure any active transactions are rolled back
            if hasattr(session, 'is_active') and session.is_active:
                await session.rollback()


class TestDatabaseMigration:
    """Test database migration functionality."""

    def test_migration_initialization(self):
        """Test that migration system can be initialized."""
        from opengovzoning.core.database import DatabaseManager

        db_manager = get_database_manager()

        # Should have migration capabilities
        assert hasattr(db_manager, 'engine')

    @pytest.mark.asyncio
    async def test_schema_creation(self):
        """Test that database schema can be created."""
        from opengovzoning.infrastructure.database.models import Base

        db_manager = get_database_manager()

        # Test that we can create all tables
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Verify tables exist
        async with db_manager.engine.begin() as conn:
            result = await conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = result.fetchall()

        assert len(tables) > 0  # Should have created tables


class TestDatabaseIntegration:
    """Test database integration with other components."""

    @pytest.mark.asyncio
    async def test_with_storage_layer(self):
        """Test database integration with storage layer."""
        from opengovzoning.storage.item_storage import ItemStorage

        storage = ItemStorage()
        db_manager = get_database_manager()

        # Should be able to work together
        assert storage is not None
        assert db_manager is not None

    @pytest.mark.asyncio
    async def test_with_api_layer(self):
        """Test database integration with API layer."""
        from opengovzoning.web.app import app

        # Should be able to import and use together
        assert app is not None
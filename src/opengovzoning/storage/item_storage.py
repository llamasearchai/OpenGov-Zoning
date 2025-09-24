"""Storage layer backed by sqlite-utils for demo purposes."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

import structlog
from sqlite_utils import Database

from ..core.config import get_settings
from ..models.item import Item, ItemCreate

logger = structlog.get_logger(__name__)


class ItemStorage:
    """Storage operations for the interactive CLI and FastAPI mock endpoints."""

    def __init__(self, db_path: Optional[str] = None):
        settings = get_settings()
        self.db_path = db_path or settings.demo_sqlite_path
        self.db = Database(self.db_path)

    def create_item(self, item: ItemCreate) -> Item:
        """Create a new item."""
        item_dict = item.dict()
        item_dict["id"] = str(item_dict["id"])
        item_dict["created_at"] = item_dict["created_at"].isoformat()
        item_dict["updated_at"] = item_dict["updated_at"].isoformat()

        self.db["items"].insert(item_dict)

        # Return as Item object
        return Item(**item_dict)

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by ID."""
        row = self.db["items"].get(item_id)
        if row:
            return self._row_to_item(row)
        return None

    def list_items(self, limit: int = 100, offset: int = 0) -> List[Item]:
        """List items with pagination."""
        rows = self.db["items"].limit(limit).offset(offset).rows
        return [self._row_to_item(row) for row in rows]

    def update_item(self, item_id: str, updates: dict) -> bool:
        """Update an item."""
        updates["updated_at"] = updates.get("updated_at", "2024-01-15T10:00:00")

        result = self.db["items"].update(item_id, updates)
        return result > 0

    def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        result = self.db["items"].delete(item_id)
        return result > 0

    def search_items(self, query: str) -> List[Item]:
        """Search items using FTS."""
        rows = self.db["items"].search(query)
        return [self._row_to_item(row) for row in rows]

    def get_item_stats(self) -> dict:
        """Get item statistics."""
        total_items = self.db["items"].count
        return {
            "total_items": total_items
        }

    def _row_to_item(self, row: dict) -> Item:
        """Convert database row to Item object."""
        row = dict(row)
        row["created_at"] = row["created_at"]
        row["updated_at"] = row["updated_at"]
        return Item(**row)
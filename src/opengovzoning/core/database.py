"""SQLite support for demo workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlite_utils import Database

from .config import get_settings


class SQLiteDatabaseManager:
    """Lightweight SQLite manager used for CLI demos and tests."""

    def __init__(self, db_path: Optional[str] = None):
        settings = get_settings()
        self.db_path = db_path or settings.demo_sqlite_path
        self.db = Database(self.db_path)

    def initialize(self, drop_existing: bool = False) -> None:
        if drop_existing and Path(self.db_path).exists():
            Path(self.db_path).unlink()

        self.db["items"].create(
            {
                "id": str,
                "name": str,
                "description": str,
                "created_at": str,
                "updated_at": str,
            },
            pk="id",
            if_not_exists=True,
        )

    def seed_sample_data(self) -> None:
        if "items" not in self.db.table_names():
            self.initialize()

        existing = {row["id"] for row in self.db["items"].rows}
        seed_rows = [
            {
                "id": "demo-1",
                "name": "Austin Solar Farm",
                "description": "Solar farm permitting baseline dataset",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            },
            {
                "id": "demo-2",
                "name": "Seattle Data Center",
                "description": "Data center compliance checklist",
                "created_at": "2025-01-02T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
            },
        ]

        for row in seed_rows:
            if row["id"] not in existing:
                self.db["items"].insert(row)

    def drop(self) -> None:
        if Path(self.db_path).exists():
            Path(self.db_path).unlink()
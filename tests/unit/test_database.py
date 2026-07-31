from __future__ import annotations

from pathlib import Path

from animax.database.connection import connect, initialize
from animax.database.schema import DB_SCHEMA_VERSION


async def test_initialize_creates_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "animax.db"
    await initialize(db_path)

    async with connect(db_path) as db:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        rows = await cursor.fetchall()
        table_names = {row["name"] for row in rows}

    assert {"schema_meta", "library_entries", "history_entries", "download_tasks"} <= table_names


async def test_initialize_records_schema_version(tmp_path: Path) -> None:
    db_path = tmp_path / "animax.db"
    await initialize(db_path)

    async with connect(db_path) as db:
        cursor = await db.execute("SELECT version FROM schema_meta")
        row = await cursor.fetchone()

    assert row is not None
    assert row["version"] == DB_SCHEMA_VERSION


async def test_initialize_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "animax.db"
    await initialize(db_path)
    await initialize(db_path)

    async with connect(db_path) as db:
        cursor = await db.execute("SELECT COUNT(*) AS count FROM schema_meta")
        row = await cursor.fetchone()

    assert row is not None
    assert row["count"] == 1

"""Async SQLite connection handling: initialization and a connect() helper."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

from animax.config.paths import database_file
from animax.core.errors import DatabaseError
from animax.database.schema import CREATE_STATEMENTS, DB_SCHEMA_VERSION


async def initialize(path: Path | None = None) -> None:
    """Create the database file and tables if they don't already exist."""
    target = path or database_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        async with aiosqlite.connect(target) as db:
            for statement in CREATE_STATEMENTS:
                await db.execute(statement)
            cursor = await db.execute("SELECT COUNT(*) FROM schema_meta")
            row = await cursor.fetchone()
            if row is not None and row[0] == 0:
                await db.execute(
                    "INSERT INTO schema_meta (version) VALUES (?)", (DB_SCHEMA_VERSION,)
                )
            await db.commit()
    except aiosqlite.Error as exc:
        raise DatabaseError(
            f"Failed to initialize the database at {target}.",
            reason=str(exc),
            fix="Check that the data directory is writable, then run `anime doctor`.",
        ) from exc


@asynccontextmanager
async def connect(path: Path | None = None) -> AsyncIterator[aiosqlite.Connection]:
    """Open a connection with row access by column name. Caller must await queries."""
    target = path or database_file()
    try:
        db = await aiosqlite.connect(target)
    except aiosqlite.Error as exc:
        raise DatabaseError(
            f"Failed to open the database at {target}.",
            reason=str(exc),
            fix="Run `anime doctor` to check database health.",
        ) from exc
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

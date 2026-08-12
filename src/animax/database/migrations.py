"""Database migration manager."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import aiosqlite

MigrationFunc = Callable[[aiosqlite.Connection], Awaitable[None]]


class MigrationManager:
    """Manages database schema migrations."""

    def __init__(self) -> None:
        self.migrations: dict[int, MigrationFunc] = {}

    def register(self, version: int, func: MigrationFunc) -> None:
        """Register a migration to reach the specified version from version - 1."""
        self.migrations[version] = func

    async def run_migrations(
        self, db: aiosqlite.Connection, current_version: int, target_version: int
    ) -> int:
        """Run all necessary migrations in order."""
        version = current_version
        while version < target_version:
            next_version = version + 1
            if next_version in self.migrations:
                # Migrations run in a transaction context if the caller wrapped it
                await self.migrations[next_version](db)
            version = next_version
            await db.execute("UPDATE schema_meta SET version = ?", (version,))
        return version


# Global manager instance
migration_manager = MigrationManager()

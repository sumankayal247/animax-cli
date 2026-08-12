import aiosqlite
import pytest

from animax.database.migrations import MigrationManager


@pytest.mark.asyncio
async def test_migration_manager_runs_in_order() -> None:
    manager = MigrationManager()

    events: list[int] = []

    async def mig_1(db: aiosqlite.Connection) -> None:
        events.append(1)

    async def mig_2(db: aiosqlite.Connection) -> None:
        events.append(2)

    manager.register(1, mig_1)
    manager.register(2, mig_2)

    async with aiosqlite.connect(":memory:") as db:
        await db.execute("CREATE TABLE schema_meta (version INTEGER NOT NULL)")
        await db.execute("INSERT INTO schema_meta (version) VALUES (0)")

        # Current version is 0, target is 2. So it should run 1 and 2.
        final_version = await manager.run_migrations(db, 0, 2)

        assert final_version == 2
        assert events == [1, 2]

        cursor = await db.execute("SELECT version FROM schema_meta LIMIT 1")
        row = await cursor.fetchone()
        assert row is not None
        assert row[0] == 2

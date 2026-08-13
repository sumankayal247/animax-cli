"""History orchestration logic."""

from __future__ import annotations

import time
from typing import Any

from animax.database.connection import connect


async def get_history(limit: int = 50) -> list[dict[str, Any]]:
    async with connect() as db:
        cursor = await db.execute("SELECT * FROM history_entries ORDER BY occurred_at DESC LIMIT ?", (limit,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def log_event(media_id: str, title: str, episode: float, event: str, plugin: str) -> None:
    now = time.time()
    async with connect() as db:
        await db.execute(
            """
            INSERT INTO history_entries (media_id, title, episode, event, occurred_at, plugin_used)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (media_id, title, episode, event, now, plugin)
        )
        await db.commit()

async def clear_history() -> None:
    async with connect() as db:
        await db.execute("DELETE FROM history_entries")
        await db.commit()

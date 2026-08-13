"""Library orchestration logic."""

from __future__ import annotations

import time
from typing import Any

from animax.database.connection import connect


async def get_library() -> list[dict[str, Any]]:
    async with connect() as db:
        cursor = await db.execute("SELECT * FROM library_entries ORDER BY last_played_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def add_to_library(media_id: str, title: str, is_favorite: bool = False) -> None:
    async with connect() as db:
        await db.execute(
            """
            INSERT INTO library_entries (media_id, title, is_favorite) 
            VALUES (?, ?, ?)
            ON CONFLICT(media_id) DO UPDATE SET 
                title=excluded.title,
                is_favorite=excluded.is_favorite
            """,
            (media_id, title, int(is_favorite))
        )
        await db.commit()

async def update_progress(media_id: str, title: str, episode: float, position: float, plugin: str) -> None:
    now = time.time()
    async with connect() as db:
        await db.execute(
            """
            INSERT INTO library_entries (media_id, title, last_episode, resume_position_seconds, last_played_at, plugin_used)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(media_id) DO UPDATE SET 
                title=excluded.title,
                last_episode=excluded.last_episode,
                resume_position_seconds=excluded.resume_position_seconds,
                last_played_at=excluded.last_played_at,
                plugin_used=excluded.plugin_used
            """,
            (media_id, title, episode, position, now, plugin)
        )
        await db.commit()

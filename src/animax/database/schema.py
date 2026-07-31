"""SQLite schema definition and its version.

DB_SCHEMA_VERSION is independent of CONFIG_SCHEMA_VERSION (core.constants)
and PLUGIN_API_VERSION — each tracks a different contract. Bump it and add
a migration step in database.connection whenever a table shape changes.
"""

from __future__ import annotations

DB_SCHEMA_VERSION = 1

CREATE_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS schema_meta (
        version INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS library_entries (
        media_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        is_favorite INTEGER NOT NULL DEFAULT 0,
        last_episode REAL,
        resume_position_seconds REAL,
        last_played_at REAL,
        plugin_used TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS history_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        media_id TEXT NOT NULL,
        title TEXT NOT NULL,
        episode REAL NOT NULL,
        event TEXT NOT NULL,
        occurred_at REAL NOT NULL,
        plugin_used TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS download_tasks (
        id TEXT PRIMARY KEY,
        media_id TEXT NOT NULL,
        episode REAL NOT NULL,
        destination TEXT NOT NULL,
        status TEXT NOT NULL,
        progress REAL NOT NULL DEFAULT 0,
        bytes_downloaded INTEGER NOT NULL DEFAULT 0,
        bytes_total INTEGER,
        retries INTEGER NOT NULL DEFAULT 0,
        error TEXT
    )
    """,
)

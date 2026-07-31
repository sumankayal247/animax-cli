# Database

SQLite via `aiosqlite`, initialized by `database.connection.initialize()`
(called from `installer.checks.check_database`, i.e. `anime doctor`).
Location: `database.database_file()` — platform data dir /
`animax.db` (see [Configuration.md](Configuration.md) for path resolution).

## Schema (`database/schema.py`, `DB_SCHEMA_VERSION = 1`)

```sql
CREATE TABLE schema_meta (
    version INTEGER NOT NULL
);

CREATE TABLE library_entries (
    media_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    is_favorite INTEGER NOT NULL DEFAULT 0,
    last_episode REAL,
    resume_position_seconds REAL,
    last_played_at REAL,
    plugin_used TEXT
);

CREATE TABLE history_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id TEXT NOT NULL,
    title TEXT NOT NULL,
    episode REAL NOT NULL,
    event TEXT NOT NULL,
    occurred_at REAL NOT NULL,
    plugin_used TEXT
);

CREATE TABLE download_tasks (
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
);
```

`library_entries` and `history_entries` correspond to
`models.library.LibraryEntry` / `HistoryEntry`; `download_tasks`
corresponds to `models.download.DownloadTask`. Query/repository helpers
that read and write these tables land in Phase 6 (`library/`) and Phase 5
(`download/`) respectively — Phase 1 only creates the schema.

## Migrations

`DB_SCHEMA_VERSION` (independent of `CONFIG_SCHEMA_VERSION` and
`PLUGIN_API_VERSION` — see [Architecture.md](Architecture.md#versioning))
is stored in `schema_meta` on first initialization. There is exactly one
version so far; a migration runner will be added in `database/` the first
time a table shape needs to change in a backward-incompatible way.

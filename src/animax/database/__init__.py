"""SQLite persistence: schema, connections, and (later) query helpers."""

from animax.database.connection import connect, initialize
from animax.database.schema import DB_SCHEMA_VERSION

__all__ = ["DB_SCHEMA_VERSION", "connect", "initialize"]

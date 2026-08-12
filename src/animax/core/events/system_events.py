"""System-level events for configuration, cache, and database lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from animax.core.events.event import Event


@dataclass(frozen=True)
class ConfigurationChangedEvent(Event):
    """Fired when the configuration is updated."""

    settings: Any


@dataclass(frozen=True)
class CacheCleanupEvent(Event):
    """Fired when a cache cleanup completes."""

    namespace: str
    items_removed: int


@dataclass(frozen=True)
class DatabaseInitializedEvent(Event):
    """Fired when the database is initialized or migrated."""

    schema_version: int
    migrated: bool

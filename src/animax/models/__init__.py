"""Shared Pydantic domain models used across core, services, and plugins."""

from animax.models.download import ContentSource, DownloadStatus, DownloadTask, SourceKind
from animax.models.library import HistoryEntry, LibraryEntry
from animax.models.media import Episode, MediaItem, SearchResult
from animax.models.plugin import (
    HealthStatus,
    PluginCategory,
    PluginInfo,
    PluginRecord,
    PluginSource,
)

__all__ = [
    "ContentSource",
    "DownloadStatus",
    "DownloadTask",
    "Episode",
    "HealthStatus",
    "HistoryEntry",
    "LibraryEntry",
    "MediaItem",
    "PluginCategory",
    "PluginInfo",
    "PluginRecord",
    "PluginSource",
    "SearchResult",
    "SourceKind",
]

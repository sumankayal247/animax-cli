"""Events related to metadata and search processes."""

from __future__ import annotations

from dataclasses import dataclass

from animax.core.events.event import Event
from animax.models.media import MediaItem


@dataclass(frozen=True)
class MetadataResolvedEvent(Event):
    """Fired when metadata for an item has been successfully resolved."""

    item: MediaItem


@dataclass(frozen=True)
class SearchStarted(Event):
    """Fired when a global search begins."""

    query: str


@dataclass(frozen=True)
class SearchCompleted(Event):
    """Fired when a global search completes."""

    query: str
    result_count: int


@dataclass(frozen=True)
class SearchNormalized(Event):
    """Fired when a search query is normalized."""

    original_query: str
    normalized_query: str


@dataclass(frozen=True)
class SearchRanked(Event):
    """Fired when search results are ranked."""

    query: str
    result_count: int


@dataclass(frozen=True)
class SuggestionsGenerated(Event):
    """Fired when search suggestions are generated."""

    query: str
    suggestions: list[str]


@dataclass(frozen=True)
class SearchAmbiguous(Event):
    """Fired when search results are ambiguous."""

    query: str
    options_count: int


@dataclass(frozen=True)
class ProviderQueryStarted(Event):
    """Fired when querying a specific metadata provider begins."""

    provider_name: str
    query: str


@dataclass(frozen=True)
class ProviderQueryCompleted(Event):
    """Fired when querying a specific metadata provider completes."""

    provider_name: str
    query: str
    result_count: int
    error: str | None = None


@dataclass(frozen=True)
class MetadataDetailsStarted(Event):
    """Fired when requesting detailed metadata."""

    item_id: str


@dataclass(frozen=True)
class MetadataDetailsCompleted(Event):
    """Fired when requesting detailed metadata completes."""

    item_id: str
    success: bool
    error: str | None = None


@dataclass(frozen=True)
class EpisodesRequested(Event):
    """Fired when requesting episode list."""

    item_id: str


@dataclass(frozen=True)
class EpisodesCompleted(Event):
    """Fired when requesting episode list completes."""

    item_id: str
    episode_count: int
    success: bool
    error: str | None = None

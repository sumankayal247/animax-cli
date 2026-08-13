"""Domain models for media items, episodes, and search results.

These are the normalized, plugin-agnostic shapes that flow between
metadata/download/streaming plugins and the rest of the application.
Individual plugins translate their provider-specific responses into these
models; nothing outside a plugin should ever see provider-native shapes.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class MediaType(Enum):
    ANIME = "Anime"
    MOVIE = "Movie"
    TV = "TV"
    MANGA = "Manga"
    NOVEL = "Novel"
    UNKNOWN = "Unknown"


class Episode(BaseModel):
    """A single episode of a media item.

    ``number`` is a float to naturally support specials/OVAs (e.g. 12.5).
    """

    number: float
    title: str | None = None
    external_id: str | None = None


class MediaItem(BaseModel):
    """A normalized media entry, merged from one or more metadata plugins."""

    id: str
    title: str
    media_type: MediaType = MediaType.ANIME
    alt_titles: list[str] = Field(default_factory=list)
    year: int | None = None
    episode_count: int | None = None
    synopsis: str | None = None
    cover_url: str | None = None
    source_plugins: list[str] = Field(default_factory=list)
    external_ids: dict[str, str] = Field(default_factory=dict)
    """Provider name -> that provider's id for this item, e.g. {"anilist": "123"}."""


class SearchResult(BaseModel):
    """A single ranked result surfaced to the search command."""

    item: MediaItem
    score: float = 1.0

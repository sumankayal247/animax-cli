"""Interface for metadata plugins (AniList, MAL, Kitsu, TMDB, ...)."""

from __future__ import annotations

from abc import abstractmethod

from animax.core.interfaces.base import BasePlugin
from animax.models.media import MediaItem, SearchResult


class MetadataPlugin(BasePlugin):
    """Looks up canonical media information for a title."""

    @abstractmethod
    async def search(self, query: str) -> list[SearchResult]:
        """Return candidate matches for a free-text query."""
        raise NotImplementedError

    @abstractmethod
    async def get_details(self, external_id: str) -> MediaItem:
        """Fetch full details for a specific item by this provider's id."""
        raise NotImplementedError

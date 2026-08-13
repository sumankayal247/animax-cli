"""Interface for search plugins: find available content for a media item.

Distinct from ``MetadataPlugin`` — metadata plugins answer "what is this
title", search plugins answer "where can I actually get episodes of it".
"""

from __future__ import annotations

from abc import abstractmethod

from animax.core.interfaces.provider import BaseProvider
from animax.models.media import MediaItem, SearchResult


class SearchProvider(BaseProvider):
    """Finds provider-specific listings for a media item."""

    @abstractmethod
    async def find(self, item: MediaItem) -> list[SearchResult]:
        """Return this provider's candidate listings for a normalized media item."""
        raise NotImplementedError

"""Interface for download plugins: resolve a downloadable file source."""

from __future__ import annotations

from abc import abstractmethod

from animax.core.interfaces.provider import BaseProvider
from animax.models.download import ContentSource
from animax.models.media import Episode, MediaItem


class DownloadProvider(BaseProvider):
    """Resolves a direct, downloadable source for a specific episode."""

    @abstractmethod
    async def resolve(self, item: MediaItem, episode: Episode) -> list[ContentSource]:
        """Return candidate download sources (e.g. one per quality) for an episode."""
        raise NotImplementedError

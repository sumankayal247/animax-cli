"""Interface for streaming plugins: resolve a playable (non-downloaded) source."""

from __future__ import annotations

from abc import abstractmethod

from animax.core.interfaces.base import BasePlugin
from animax.models.download import ContentSource
from animax.models.media import Episode, MediaItem


class StreamingPlugin(BasePlugin):
    """Resolves a direct-play source for a specific episode, for local playback."""

    @abstractmethod
    async def resolve(self, item: MediaItem, episode: Episode) -> list[ContentSource]:
        """Return candidate stream sources (e.g. one per quality) for an episode."""
        raise NotImplementedError

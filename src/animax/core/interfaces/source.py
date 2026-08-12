"""Source Provider Interface.

Defines the interface for plugins that resolve downloadable/streamable
sources (ContentSource) for a given media item and episode.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from animax.core.interfaces.base import BasePlugin

if TYPE_CHECKING:
    from animax.models.download import ContentSource
    from animax.models.media import MediaItem


class SourcePlugin(BasePlugin):
    """Base class for plugins that resolve video sources."""

    @abc.abstractmethod
    async def resolve_source(
        self,
        media: MediaItem,
        episode_num: float,
        quality: str | None = None,
    ) -> list[ContentSource]:
        """Resolve a media item and episode into streamable/downloadable sources.

        Args:
            media: The media item (e.g. from a metadata search).
            episode_num: The episode number.
            quality: Optional preferred quality (e.g. '1080p', '720p').

        Returns:
            A list of valid ContentSource objects, ideally sorted by best match.
        """
        pass

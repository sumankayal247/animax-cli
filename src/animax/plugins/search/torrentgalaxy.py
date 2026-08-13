"""TorrentGalaxy General Torrent Provider."""

from __future__ import annotations

import httpx

from animax.core.interfaces.search import SearchProvider
from animax.models.download import ContentSource
from animax.models.media import MediaItem, SearchResult
from animax.models.provider import ProviderCapabilities, ProviderCategory, ProviderInfo


class TorrentGalaxyProvider(SearchProvider):
    """Searches TorrentGalaxy for torrents."""

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="TorrentGalaxy",
            description="General Torrent search provider using TorrentGalaxy",
            category=ProviderCategory.SOURCE,
            priority=80,
            capabilities=ProviderCapabilities(search=True, download=True, magnet=True),
        )

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://torrentgalaxy.to/", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    async def resolve_source(
        self, media: MediaItem, episode_num: float, quality: str | None = None
    ) -> list[ContentSource]:
        """Resolve a media item and episode into magnet links."""
        # TODO: Implement TorrentGalaxy HTML scraping in Phase 5
        return []

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

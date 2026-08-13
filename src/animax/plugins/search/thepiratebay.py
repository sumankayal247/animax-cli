"""The Pirate Bay General Torrent Provider."""

from __future__ import annotations

import httpx

from animax.core.interfaces.search import SearchProvider
from animax.models.download import ContentSource
from animax.models.media import MediaItem, SearchResult
from animax.models.provider import ProviderCapabilities, ProviderCategory, ProviderInfo

_BASE_URL = "https://apibay.org/q.php"


class ThePirateBayProvider(SearchProvider):
    """Searches The Pirate Bay for torrents."""

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="The Pirate Bay",
            description="General Torrent search provider using TPB",
            category=ProviderCategory.SOURCE,
            priority=70,
            capabilities=ProviderCapabilities(search=True, download=True, magnet=True),
        )

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://thepiratebay.org/", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    async def resolve_source(
        self, media: MediaItem, episode_num: float, quality: str | None = None
    ) -> list[ContentSource]:
        """Resolve a media item and episode into magnet links."""
        # TODO: Implement TPB HTML scraping in Phase 5
        return []

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

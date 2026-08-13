"""AnimeTosho Anime Torrent Provider."""

from __future__ import annotations

import httpx

from animax.core.interfaces.search import SearchProvider
from animax.models.download import ContentSource
from animax.models.media import MediaItem, SearchResult
from animax.models.provider import ProviderCapabilities, ProviderCategory, ProviderInfo


class AnimeToshoProvider(SearchProvider):
    """Searches AnimeTosho for torrents."""

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="AnimeTosho",
            description="Anime Torrent search provider using AnimeTosho",
            category=ProviderCategory.SOURCE,
            priority=55,
            capabilities=ProviderCapabilities(search=True, download=True, magnet=True),
        )

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://animetosho.org/", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    async def resolve_source(
        self, media: MediaItem, episode_num: float, quality: str | None = None
    ) -> list[ContentSource]:
        """Resolve a media item and episode into magnet links."""
        # TODO: Implement AnimeTosho HTML/API scraping in Phase 5
        return []

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

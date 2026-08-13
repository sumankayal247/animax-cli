"""AnimeTosho Anime Torrent Provider."""

from __future__ import annotations

import httpx

from animax.core.interfaces.source import SourcePlugin
from animax.models.download import ContentSource, SourceKind
from animax.models.media import MediaItem
from animax.models.plugin import PluginCategory, PluginInfo, ProviderCapabilities


class AnimeToshoProvider(SourcePlugin):
    """Searches AnimeTosho for torrents."""

    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="AnimeTosho",
            version="1.0.0",
            author="animax-cli",
            description="Anime Torrent search provider using AnimeTosho",
            category=PluginCategory.SOURCE,
            api_version="1.0.0",
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

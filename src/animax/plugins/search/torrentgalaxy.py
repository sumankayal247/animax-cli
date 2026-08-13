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
        from animax.models.media import MediaType
        import urllib.parse
        import re
        from animax.models.download import SourceKind

        clean_title = re.sub(r'[^\w\s]', '', media.title)
        query = clean_title
        if media.media_type != MediaType.MOVIE:
            query += f" {int(episode_num):02d}"
        if quality:
            query += f" {quality}"

        url = "https://torrentgalaxy.to/torrents.php?search=" + urllib.parse.quote(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        sources: list[ContentSource] = []
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code == 200:
                    # TorrentGalaxy often lists magnets directly on the search results page!
                    magnets = re.findall(r'href="(magnet:\?xt=urn:btih:[a-zA-Z0-9]+[^"]*)"', resp.text)
                    for magnet in magnets:
                        sources.append(ContentSource(
                            url=magnet,
                            kind=SourceKind.DOWNLOAD,
                            quality=quality or "unknown",
                            plugin="TorrentGalaxy",
                        ))
                        if len(sources) >= 3:
                            break
            except Exception:
                pass
                
        return sources

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

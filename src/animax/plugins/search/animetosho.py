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
        from animax.models.media import MediaType
        import urllib.parse
        import re
        import xml.etree.ElementTree as ET
        from animax.models.download import SourceKind

        clean_title = re.sub(r'[^\w\s]', '', media.title)
        query = clean_title
        if media.media_type != MediaType.MOVIE:
            query += f" {int(episode_num):02d}"
        if quality:
            query += f" {quality}"

        url = "https://feed.animetosho.org/rss2?q=" + urllib.parse.quote(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(headers=headers) as client:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code != 200:
                return []
                
        root = ET.fromstring(resp.text)
        sources: list[ContentSource] = []
        
        for item in root.findall("./channel/item"):
            # AnimeTosho puts magnet links in enclosure or link
            magnet = ""
            for enc in item.findall("enclosure"):
                if enc.get("url", "").startswith("magnet:"):
                    magnet = enc.get("url")
                    break
            
            if not magnet:
                link = item.findtext("link")
                if link and link.startswith("magnet:"):
                    magnet = link
                    
            if magnet:
                sources.append(
                    ContentSource(
                        url=magnet,
                        kind=SourceKind.DOWNLOAD,
                        quality=quality or "unknown",
                        plugin="AnimeTosho",
                    )
                )
                
        return sources

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

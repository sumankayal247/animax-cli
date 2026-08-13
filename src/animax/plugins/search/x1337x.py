"""1337x General Torrent Provider."""

from __future__ import annotations

import httpx

from animax.core.interfaces.search import SearchProvider
from animax.models.download import ContentSource
from animax.models.media import MediaItem, SearchResult
from animax.models.provider import ProviderCapabilities, ProviderCategory, ProviderInfo


class Torrent1337xProvider(SearchProvider):
    """Searches 1337x.to for torrents."""

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="1337x",
            description="General Torrent search provider using 1337x",
            category=ProviderCategory.SOURCE,
            priority=60,
            capabilities=ProviderCapabilities(search=True, download=True, magnet=True),
        )

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://1337x.to/", timeout=5.0)
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

        url = "https://1337x.to/search/" + urllib.parse.quote(query) + "/1/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code != 200:
                    return []
                    
                # 1337x search results just link to torrent pages, which have the magnet.
                # To make it fast without double-requesting, we can check if the search page
                # itself exposes magnets (it usually doesn't).
                # Actually, an easier alternative is x1337x API if available, 
                # but for now we just scrape the first torrent page link we find.
                torrent_link_match = re.search(r'href="(/torrent/[^"]+)"', resp.text)
                if not torrent_link_match:
                    return []
                    
                torrent_url = "https://1337x.to" + torrent_link_match.group(1)
                t_resp = await client.get(torrent_url, timeout=10.0)
                magnet_match = re.search(r'(magnet:\?xt=urn:btih:[a-zA-Z0-9]+[^"]*)', t_resp.text)
                
                if magnet_match:
                    return [ContentSource(
                        url=magnet_match.group(1),
                        kind=SourceKind.DOWNLOAD,
                        quality=quality or "unknown",
                        plugin="1337x",
                    )]
            except Exception:
                pass
                
        return []

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

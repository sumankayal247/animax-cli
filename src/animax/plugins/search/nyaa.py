"""Nyaa Anime Torrent Provider."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from animax.core.interfaces.search import SearchProvider
from animax.models.download import ContentSource, SourceKind
from animax.models.media import MediaItem, SearchResult
from animax.models.provider import ProviderCapabilities, ProviderCategory, ProviderInfo


class NyaaProvider(SearchProvider):
    """Searches Nyaa.si for anime torrents."""

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="Nyaa",
            description="Anime Torrent search provider using Nyaa.si RSS",
            category=ProviderCategory.SOURCE,
            priority=50,
            capabilities=ProviderCapabilities(search=True, download=True, magnet=True),
        )

    async def check_health(self) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://nyaa.iss.one/", timeout=5.0)
            return resp.status_code == 200

    async def resolve_source(
        self, media: MediaItem, episode_num: float, quality: str | None = None
    ) -> list[ContentSource]:
        """Resolve a media item and episode into magnet links."""
        from animax.models.media import MediaType
        import re
        
        # Remove special characters that might break search
        clean_title = re.sub(r'[^\w\s]', '', media.title)
        query = clean_title
        
        if media.media_type != MediaType.MOVIE:
            query += f" {int(episode_num):02d}"
            
        if quality:
            query += f" {quality}"

        import urllib.parse
        url = "https://nyaa.iss.one/?page=rss&q=" + urllib.parse.quote(query) + "&c=1_2&f=0"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            
        root = ET.fromstring(resp.text)
        sources: list[ContentSource] = []
        
        for item in root.findall("./channel/item"):
            link = item.findtext("link")
            
            # Find the magnet link
            magnet = ""
            if link and link.startswith("magnet:"):
                magnet = link
            else:
                # Nyaa RSS usually puts torrent file URL in link.
                magnet = link
                
            if magnet:
                sources.append(
                    ContentSource(
                        url=magnet,
                        kind=SourceKind.DOWNLOAD,
                        quality=quality or "unknown",
                        plugin="Nyaa",
                    )
                )
                
        return sources

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

"""Nyaa Anime Torrent Provider."""

from __future__ import annotations

import httpx
import xml.etree.ElementTree as ET

from animax.core.interfaces.source import SourcePlugin
from animax.models.download import ContentSource, SourceKind
from animax.models.media import MediaItem
from animax.models.plugin import PluginCategory, PluginInfo, ProviderCapabilities


class NyaaProvider(SourcePlugin):
    """Searches Nyaa.si for anime torrents."""

    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="Nyaa",
            version="1.0.0",
            author="animax-cli",
            description="Anime Torrent search provider using Nyaa.si RSS",
            category=PluginCategory.SOURCE,
            api_version="1.0.0",
            priority=50,
            capabilities=ProviderCapabilities(search=True, download=True, magnet=True),
        )

    async def check_health(self) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://nyaa.si/", timeout=5.0)
            return resp.status_code == 200

    async def resolve_source(
        self, media: MediaItem, episode_num: float, quality: str | None = None
    ) -> list[ContentSource]:
        """Resolve a media item and episode into magnet links."""
        # Clean title for search
        query = f"{media.title} {int(episode_num):02d}"
        if quality:
            query += f" {quality}"

        url = "https://nyaa.si/?page=rss&q=" + httpx.utils.quote(query) + "&c=1_2&f=0"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            
        root = ET.fromstring(resp.text)
        sources: list[ContentSource] = []
        
        for item in root.findall("./channel/item"):
            title = item.findtext("title")
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

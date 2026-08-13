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

        url = "https://apibay.org/q.php?q=" + urllib.parse.quote(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        sources: list[ContentSource] = []
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data:
                        info_hash = item.get("info_hash")
                        name = item.get("name")
                        if info_hash and info_hash != "0000000000000000000000000000000000000000":
                            # Use DNS over HTTPS (DoH) to bypass ISP DNS blocking
                            # We resolve the trackers dynamically to their raw IPs
                            import asyncio
                            
                            async def resolve_tracker(domain: str, port: int, client) -> str | None:
                                try:
                                    doh_url = f"https://dns.google/resolve?name={domain}&type=A"
                                    r = await client.get(doh_url, timeout=3.0)
                                    ans = r.json().get("Answer", [])
                                    if ans:
                                        ip = ans[0].get("data")
                                        if ip:
                                            # Using raw IP for UDP completely bypasses DNS and SNI checks
                                            return f"&tr=udp%3A%2F%2F{ip}%3A{port}%2Fannounce"
                                except Exception:
                                    pass
                                return None

                            trackers_to_resolve = [
                                ("tracker.opentrackr.org", 1337),
                                ("open.stealth.si", 80),
                                ("tracker.torrent.eu.org", 451),
                                ("explodie.org", 6969),
                            ]
                            
                            tasks = [resolve_tracker(d, p, client) for d, p in trackers_to_resolve]
                            resolved = await asyncio.gather(*tasks)
                            
                            trackers = "".join([t for t in resolved if t])
                            # Also append WSS trackers which use standard HTTPS and are rarely blocked
                            trackers += "&tr=wss%3A%2F%2Ftracker.btorrent.xyz&tr=wss%3A%2F%2Ftracker.openwebtorrent.com"
                            
                            magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(name)}{trackers}"
                            sources.append(ContentSource(
                                url=magnet,
                                kind=SourceKind.DOWNLOAD,
                                quality=quality or "unknown",
                                plugin="The Pirate Bay",
                            ))
                            # We just grab the top 3 results to save processing
                            if len(sources) >= 3:
                                break
            except Exception:
                pass
                
        return sources

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

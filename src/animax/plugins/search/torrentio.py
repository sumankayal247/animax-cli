"""Torrentio Meta-Search Provider."""

from __future__ import annotations

import httpx

from animax.core.interfaces.search import SearchProvider
from animax.models.download import ContentSource
from animax.models.media import MediaItem, SearchResult
from animax.models.provider import ProviderCapabilities, ProviderCategory, ProviderInfo


class TorrentioProvider(SearchProvider):
    """Searches Torrentio for magnet links (aggregates YTS, 1337x, TPB, etc.)."""

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="Torrentio",
            description="Aggregates torrents from 1337x, PirateBay, YTS, EZTV, and more via Torrentio.",
            category=ProviderCategory.SOURCE,
            priority=45,
            capabilities=ProviderCapabilities(search=True, download=True, magnet=True),
        )

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://torrentio.strem.fun/manifest.json", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False

    async def resolve_source(
        self, media: MediaItem, episode_num: float, quality: str | None = None
    ) -> list[ContentSource]:
        from animax.models.media import MediaType
        from animax.models.download import SourceKind
        import urllib.parse
        import asyncio

        imdb_id = media.external_ids.get("imdb")
        if not imdb_id:
            return []

        if media.media_type == MediaType.MOVIE:
            url = f"https://torrentio.strem.fun/stream/movie/{imdb_id}.json"
        else:
            # Assuming season 1 for now, a proper implementation would map episode_num to season/episode
            # if we have that metadata, but let's assume S01E{episode_num}
            url = f"https://torrentio.strem.fun/stream/series/{imdb_id}:1:{int(episode_num)}.json"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        sources: list[ContentSource] = []
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    streams = data.get("streams", [])
                    
                    # Fetch DoH trackers for bypassing ISP block
                    async def resolve_tracker(domain: str, port: int) -> str | None:
                        try:
                            doh_url = f"https://dns.google/resolve?name={domain}&type=A"
                            r = await client.get(doh_url, timeout=3.0)
                            ans = r.json().get("Answer", [])
                            if ans:
                                ip = ans[0].get("data")
                                if ip:
                                    return f"&tr=udp%3A%2F%2F{ip}%3A{port}%2Fannounce"
                        except Exception:
                            pass
                        return None
                        
                    trackers_to_resolve = [
                        ("tracker.opentrackr.org", 1337),
                        ("open.stealth.si", 80),
                        ("tracker.torrent.eu.org", 451),
                    ]
                    resolved = await asyncio.gather(*[resolve_tracker(d, p) for d, p in trackers_to_resolve])
                    trackers = "".join([t for t in resolved if t])
                    trackers += "&tr=wss%3A%2F%2Ftracker.btorrent.xyz&tr=wss%3A%2F%2Ftracker.openwebtorrent.com"

                    for stream in streams:
                        info_hash = stream.get("infoHash")
                        title = stream.get("title", "")
                        
                        if info_hash:
                            magnet = f"magnet:?xt=urn:btih:{info_hash}{trackers}"
                            sources.append(ContentSource(
                                url=magnet,
                                kind=SourceKind.DOWNLOAD,
                                quality=quality or "unknown",
                                plugin="Torrentio",
                            ))
                            
                        if len(sources) >= 5:
                            break
            except Exception:
                pass
                
        return sources

    async def find(self, item: MediaItem) -> list[SearchResult]:
        return []

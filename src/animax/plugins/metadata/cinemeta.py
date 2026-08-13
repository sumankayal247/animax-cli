"""Cinemeta general movie/TV metadata plugin."""

from __future__ import annotations

import contextlib
import httpx

from animax.core.interfaces.metadata import MetadataProvider
from animax.models.media import Episode, MediaItem, MediaType, SearchResult
from animax.models.provider import ProviderCapabilities, ProviderCategory, ProviderInfo


def _map_cinemeta_type(media_type: str | None) -> MediaType:
    if not media_type:
        return MediaType.UNKNOWN
    if media_type == "movie":
        return MediaType.MOVIE
    if media_type == "series":
        return MediaType.TV
    return MediaType.UNKNOWN


class CinemetaProvider(MetadataProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="cinemeta",
            description="Fetches general movie and TV metadata from Cinemeta.",
            category=ProviderCategory.METADATA,
            priority=10,
            capabilities=ProviderCapabilities(search=True, metadata=True, episodes=True)
        )

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://v3-cinemeta.strem.io/catalog/movie/top.json",
                    timeout=5.0,
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def search(self, query: str) -> list[SearchResult]:
        try:
            # Search movies and series concurrently
            async with httpx.AsyncClient(follow_redirects=True) as client:
                m_resp = await client.get(f"https://v3-cinemeta.strem.io/catalog/movie/top/search={query}.json", timeout=10.0)
                s_resp = await client.get(f"https://v3-cinemeta.strem.io/catalog/series/top/search={query}.json", timeout=10.0)
                
                m_data = m_resp.json().get("metas", []) if m_resp.status_code == 200 else []
                s_data = s_resp.json().get("metas", []) if s_resp.status_code == 200 else []
                
                media_list = m_data + s_data

                results = []
                for m in media_list:
                    title = m.get("name") or "Unknown"
                    year = None
                    if m.get("releaseInfo"):
                        with contextlib.suppress(ValueError):
                            year = int(str(m["releaseInfo"]).split("-")[0])

                    internal_id = f"{m.get('type', 'movie')}:{m.get('id')}"

                    item = MediaItem(
                        id=internal_id,
                        title=title,
                        alt_titles=[],
                        media_type=_map_cinemeta_type(m.get("type")),
                        year=year,
                        cover_url=m.get("poster"),
                        source_plugins=["cinemeta"],
                        external_ids={"cinemeta": internal_id, "imdb": m.get("imdb_id") or m.get("id")},
                    )
                    results.append(SearchResult(item=item, score=1.0))
                return results
        except Exception:
            return []

    async def get_details(self, external_id: str) -> MediaItem:
        if ":" in external_id:
            m_type, m_id = external_id.split(":", 1)
        else:
            m_type, m_id = "movie", external_id
            
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(
                f"https://v3-cinemeta.strem.io/meta/{m_type}/{m_id}.json",
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            meta = data.get("meta", {})
            if not meta:
                raise RuntimeError("Not found")

            title = meta.get("name") or "Unknown"
            year = None
            if meta.get("releaseInfo"):
                with contextlib.suppress(ValueError):
                    year = int(str(meta["releaseInfo"]).split("-")[0])
                    
            ep_count = None
            if meta.get("type") == "series":
                episodes = meta.get("videos", [])
                if episodes:
                    ep_count = len(episodes)

            return MediaItem(
                id=external_id,
                title=title,
                alt_titles=[],
                media_type=_map_cinemeta_type(meta.get("type")),
                year=year,
                episode_count=ep_count,
                synopsis=meta.get("description"),
                cover_url=meta.get("poster"),
                source_plugins=["cinemeta"],
                external_ids={"cinemeta": external_id, "imdb": m_id},
            )

    async def get_episodes(self, external_id: str) -> list[Episode]:
        if ":" in external_id:
            m_type, m_id = external_id.split(":", 1)
        else:
            m_type, m_id = "series", external_id
            
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                resp = await client.get(
                    f"https://v3-cinemeta.strem.io/meta/{m_type}/{m_id}.json",
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
                meta = data.get("meta", {})
                
                episodes = []
                # Stremio uses 'videos' array for episodes
                for idx, v in enumerate(meta.get("videos", [])):
                    episodes.append(
                        Episode(
                            number=float(v.get("episode", idx + 1)),
                            title=v.get("name") or f"Episode {v.get('episode')}",
                            external_id=v.get("id"),
                        )
                    )
                return episodes
        except Exception:
            return []

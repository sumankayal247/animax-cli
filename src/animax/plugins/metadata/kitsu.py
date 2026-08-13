"""Kitsu metadata plugin."""

from __future__ import annotations

import contextlib

import httpx

from animax.core.interfaces.metadata import MetadataPlugin
from animax.models.media import Episode, MediaItem, MediaType, SearchResult
from animax.models.plugin import PluginCategory, PluginInfo, ProviderCapabilities


def _map_kitsu_subtype(subtype: str | None) -> MediaType:
    if not subtype:
        return MediaType.UNKNOWN
    subtype = subtype.upper()
    match subtype:
        case "TV":
            return MediaType.TV
        case "MOVIE":
            return MediaType.MOVIE
        case "OVA":
            return MediaType.OVA
        case "ONA":
            return MediaType.ONA
        case "SPECIAL":
            return MediaType.SPECIAL
        case "MUSIC":
            return MediaType.MUSIC
        case _:
            return MediaType.UNKNOWN


class KitsuPlugin(MetadataPlugin):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="kitsu",
            version="1.0.0",
            category=PluginCategory.METADATA,
            api_version="1.0.0",
            author="animax",
            capabilities=ProviderCapabilities(metadata=True, search=True),
            description="Fetches metadata from Kitsu REST API.",
        )

    @property
    def capabilities(self) -> set[str]:
        return {"search", "details", "episodes"}

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://kitsu.io/api/edge/anime?page[limit]=1",
                    timeout=5.0,
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def search(self, query: str) -> list[SearchResult]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://kitsu.io/api/edge/anime?filter[text]={query}",
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
                media_list = data.get("data", [])

                results = []
                for m in media_list:
                    attrs = m.get("attributes", {})
                    titles = attrs.get("titles", {})
                    title = (
                        titles.get("en")
                        or titles.get("en_jp")
                        or attrs.get("canonicalTitle")
                        or "Unknown"
                    )

                    alt_titles = []
                    if "en_jp" in titles and titles["en_jp"] != title:
                        alt_titles.append(titles["en_jp"])
                    if "ja_jp" in titles and titles["ja_jp"] != title:
                        alt_titles.append(titles["ja_jp"])

                    year = None
                    if attrs.get("startDate"):
                        with contextlib.suppress(ValueError):
                            year = int(attrs["startDate"].split("-")[0])

                    item = MediaItem(
                        id=str(m["id"]),
                        title=title,
                        alt_titles=tuple(alt_titles),
                        media_type=_map_kitsu_subtype(attrs.get("subtype")),
                        year=year,
                        season=None,
                        studio=None,  # Kitsu relationships needed for studio/genres, omitting
                        genres=tuple(),
                        episode_count=attrs.get("episodeCount"),
                        synopsis=attrs.get("synopsis"),
                        cover_url=attrs.get("posterImage", {}).get("large"),
                        source_plugins=("kitsu",),
                        external_ids={"kitsu": str(m["id"])},
                    )
                    results.append(SearchResult(item=item, score=1.0))
                return results
        except Exception:
            return []

    async def get_details(self, external_id: str) -> MediaItem:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://kitsu.io/api/edge/anime/{external_id}",
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            m = data.get("data", {})
            if not m:
                raise RuntimeError("Not found")

            attrs = m.get("attributes", {})
            titles = attrs.get("titles", {})
            title = (
                titles.get("en") or titles.get("en_jp") or attrs.get("canonicalTitle") or "Unknown"
            )

            alt_titles = []
            if "en_jp" in titles and titles["en_jp"] != title:
                alt_titles.append(titles["en_jp"])
            if "ja_jp" in titles and titles["ja_jp"] != title:
                alt_titles.append(titles["ja_jp"])

            year = None
            if attrs.get("startDate"):
                with contextlib.suppress(ValueError):
                    year = int(attrs["startDate"].split("-")[0])

            return MediaItem(
                id=str(m["id"]),
                title=title,
                alt_titles=tuple(alt_titles),
                media_type=_map_kitsu_subtype(attrs.get("subtype")),
                year=year,
                season=None,
                studio=None,
                genres=tuple(),
                episode_count=attrs.get("episodeCount"),
                synopsis=attrs.get("synopsis"),
                cover_url=attrs.get("posterImage", {}).get("large"),
                source_plugins=("kitsu",),
                external_ids={"kitsu": str(m["id"])},
            )

    async def get_episodes(self, external_id: str) -> list[Episode]:
        # Fetching episodes from Kitsu
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://kitsu.io/api/edge/anime/{external_id}/episodes",
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
                episodes = []
                for ep in data.get("data", []):
                    attrs = ep.get("attributes", {})
                    episodes.append(
                        Episode(
                            number=float(attrs.get("number", 0)),
                            title=attrs.get("canonicalTitle"),
                            external_id=str(ep["id"]),
                            synopsis=attrs.get("synopsis"),
                            duration_minutes=attrs.get("length"),
                        )
                    )
                return episodes
        except Exception:
            return []

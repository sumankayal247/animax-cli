"""AniList metadata plugin."""

from __future__ import annotations

import httpx

from animax.core.interfaces.metadata import MetadataProvider
from animax.models.media import Episode, MediaItem, MediaType, SearchResult
from animax.models.provider import ProviderCapabilities, ProviderCategory, ProviderInfo


def _map_anilist_format(fmt: str | None) -> MediaType:
    match fmt:
        case "TV" | "TV_SHORT":
            return MediaType.TV
        case "MOVIE":
            return MediaType.MOVIE
        case "OVA":
            return MediaType.UNKNOWN
        case "ONA":
            return MediaType.UNKNOWN
        case "SPECIAL":
            return MediaType.UNKNOWN
        case "MUSIC":
            return MediaType.UNKNOWN
        case _:
            return MediaType.UNKNOWN


class AniListProvider(MetadataProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="anilist",
            description="Fetches metadata from AniList.",
            category=ProviderCategory.METADATA,
            capabilities=ProviderCapabilities(
                search=True,
                metadata=True,
                episodes=True
            )
        )

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://graphql.anilist.co",
                    json={"query": "{ SiteStatistics { anime { count } } }"},
                    timeout=5.0,
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def search(self, query: str) -> list[SearchResult]:
        query_str = """
        query ($search: String) {
          Page(page: 1, perPage: 25) {
            media(search: $search, type: ANIME) {
              id
              title { romaji english }
              seasonYear
              episodes
              description
              coverImage { extraLarge }
              season
              studios(isMain: true) { nodes { name } }
              genres
              format
            }
          }
        }
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://graphql.anilist.co",
                    json={"query": query_str, "variables": {"search": query}},
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
                media_list = data.get("data", {}).get("Page", {}).get("media", [])

                results = []
                for m in media_list:
                    title = (
                        m.get("title", {}).get("english")
                        or m.get("title", {}).get("romaji")
                        or "Unknown"
                    )
                    alt_titles = []
                    romaji = m.get("title", {}).get("romaji")
                    if romaji and romaji != title:
                        alt_titles.append(romaji)

                    studios = m.get("studios", {}).get("nodes", [])
                    studio_name = studios[0].get("name") if studios else None

                    item = MediaItem(
                        id=str(m["id"]),
                        title=title,
                        alt_titles=list(alt_titles),
                        media_type=_map_anilist_format(m.get("format")),
                        year=m.get("seasonYear"),
                        episode_count=m.get("episodes"),
                        cover_url=m.get("coverImage", {}).get("extraLarge"),
                        source_plugins=["anilist",],
                        external_ids={"anilist": str(m["id"])},
                    )
                    results.append(SearchResult(item=item, score=1.0))
                return results
        except Exception:
            return []

    async def get_details(self, external_id: str) -> MediaItem:
        query_str = """
        query ($id: Int) {
          Media(id: $id, type: ANIME) {
            id
            title { romaji english }
            seasonYear
            episodes
            description
            coverImage { extraLarge }
            season
            studios(isMain: true) { nodes { name } }
            genres
            format
            characters(sort: ROLE, perPage: 5) { nodes { name { full } } }
          }
        }
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://graphql.anilist.co",
                json={"query": query_str, "variables": {"id": int(external_id)}},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            m = data.get("data", {}).get("Media", {})
            if not m:
                raise RuntimeError("Not found")

            title = (
                m.get("title", {}).get("english") or m.get("title", {}).get("romaji") or "Unknown"
            )
            alt_titles = []
            romaji = m.get("title", {}).get("romaji")
            if romaji and romaji != title:
                alt_titles.append(romaji)

            studios = m.get("studios", {}).get("nodes", [])
            studio_name = studios[0].get("name") if studios else None

            chars = [
                c.get("name", {}).get("full")
                for c in m.get("characters", {}).get("nodes", [])
                if c.get("name", {}).get("full")
            ]

            return MediaItem(
                id=str(m["id"]),
                title=title,
                alt_titles=list(alt_titles),
                media_type=_map_anilist_format(m.get("format")),
                year=m.get("seasonYear"),
                episode_count=m.get("episodes"),
                cover_url=m.get("coverImage", {}).get("extraLarge"),
                source_plugins=["anilist",],
                external_ids={"anilist": str(m["id"])},
            )

    async def get_episodes(self, external_id: str) -> list[Episode]:
        # AniList doesn't provide detailed episode lists via GraphQL easily without streaming links,
        # but we can return dummy episodes up to episode_count
        try:
            item = await self.get_details(external_id)
            count = item.episode_count or 0
            episodes = []
            for i in range(1, count + 1):
                episodes.append(Episode(number=float(i), title=f"Episode {i}"))
            return episodes
        except Exception:
            return []




from __future__ import annotations

from typing import Any

import pytest

from animax.core.errors import ServiceError
from animax.core.interfaces.metadata import MetadataPlugin
from animax.core.interfaces.search import SearchPlugin
from animax.models.media import MediaItem, SearchResult
from animax.models.plugin import PluginCategory, PluginInfo, PluginRecord, PluginSource
from animax.services.metadata_service import resolve_query
from animax.services.search_service import search


class FakeMetadataPlugin(MetadataPlugin):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="fake_meta",
            version="1.0",
            category=PluginCategory.METADATA,
            api_version="1.0.0",
            author="test",
            description="test",
        )

    async def get_details(self, media_id: str) -> MediaItem:
        return MediaItem(id=media_id, title="Details", year=1999)

    async def search(self, query: str) -> list[SearchResult]:
        if query == "One Piece":
            item = MediaItem(id="1", title="One Piece", year=1999)
            return [SearchResult(item=item)]
        return []

    async def get_episodes(self, external_id: str) -> list[Any]:
        return []

    async def check_health(self) -> bool:
        return True

    @property
    def capabilities(self) -> set[str]:
        return {"search", "details", "episodes"}


class FakeSearchPlugin(SearchPlugin):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="fake_search",
            version="1.0",
            category=PluginCategory.SEARCH,
            api_version="1.0.0",
            author="test",
            description="test",
        )

    async def find(self, item: MediaItem) -> list[SearchResult]:
        if item.title == "One Piece":
            return [SearchResult(item=item)]
        raise RuntimeError("Not found")


@pytest.fixture
def fake_plugin_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    info_meta = PluginInfo(
        name="fake_meta",
        version="1.0",
        category=PluginCategory.METADATA,
        api_version="1.0.0",
        author="test",
        description="test",
    )
    info_search = PluginInfo(
        name="fake_search",
        version="1.0",
        category=PluginCategory.SEARCH,
        api_version="1.0.0",
        author="test",
        description="test",
    )

    rec_meta = PluginRecord(
        info=info_meta, instance=FakeMetadataPlugin(), source=PluginSource.BUILTIN
    )
    rec_search = PluginRecord(
        info=info_search, instance=FakeSearchPlugin(), source=PluginSource.BUILTIN
    )

    async def mock_discover() -> tuple[list[PluginRecord], list[str]]:
        return [rec_meta, rec_search], []

    monkeypatch.setattr("animax.services.metadata_service.discover_plugins", mock_discover)
    monkeypatch.setattr("animax.services.search_service.discover_plugins", mock_discover)


@pytest.mark.asyncio
async def test_resolve_query_metadata(fake_plugin_manager: None) -> None:
    results = await resolve_query("One Piece")
    assert len(results) == 1
    assert results[0].item.title == "One Piece"


@pytest.mark.asyncio
async def test_search_service_found(fake_plugin_manager: None) -> None:
    results = await search("One Piece")
    assert len(results) == 1
    assert results[0].item.title == "One Piece"


@pytest.mark.asyncio
async def test_search_service_not_found(fake_plugin_manager: None) -> None:
    with pytest.raises(ServiceError) as exc:
        await search("Naruto")
    assert "No results found" in str(exc.value)

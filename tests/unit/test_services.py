from __future__ import annotations

from typing import Any

import pytest

from animax.core.errors import ServiceError
from animax.core.interfaces.metadata import MetadataProvider
from animax.core.interfaces.search import SearchProvider
from animax.models.media import MediaItem, SearchResult
from animax.models.provider import ProviderCategory, ProviderInfo, ProviderRecord
from animax.services.metadata_service import resolve_query
from animax.services.search_service import search


class FakeMetadataProvider(MetadataProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="fake_meta",
            category=ProviderCategory.METADATA,
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


class FakeSearchProvider(SearchProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="fake_search",
            category=ProviderCategory.SEARCH,
            description="test",
        )

    async def find(self, item: MediaItem) -> list[SearchResult]:
        if item.title == "One Piece":
            return [SearchResult(item=item)]
        raise RuntimeError("Not found")


@pytest.fixture
def fake_plugin_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    info_meta = ProviderInfo(
        name="fake_meta",
        category=ProviderCategory.METADATA,
        description="test",
    )
    info_search = ProviderInfo(
        name="fake_search",
        category=ProviderCategory.SEARCH,
        description="test",
    )

    rec_meta = ProviderRecord(
        info=info_meta, instance=FakeMetadataProvider(), plugin_name="animax_builtin"
    )
    rec_search = ProviderRecord(
        info=info_search, instance=FakeSearchProvider(), plugin_name="animax_builtin"
    )

    async def mock_discover() -> tuple[list[Any], list[str]]:
        return [], []

    class MockRegistry:
        def enabled(self):
            return [rec_meta, rec_search]
            
    monkeypatch.setattr("animax.services.metadata_service.discover_plugins", mock_discover)
    monkeypatch.setattr("animax.services.search_service.discover_plugins", mock_discover)
    
    monkeypatch.setattr("animax.services.metadata_service.get_provider_registry", lambda: MockRegistry())
    monkeypatch.setattr("animax.services.search_service.get_provider_registry", lambda: MockRegistry())


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

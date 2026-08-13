from __future__ import annotations

from typing import Any

import pytest

from animax.core.events import (
    EventBus,
    ProviderHealthChangedEvent,
    ProviderLoadedEvent,
    ProviderRejectedEvent,
)
from animax.core.interfaces.base import BasePlugin
from animax.core.plugin_manager import PluginManager
from animax.models.media import MediaItem, SearchResult
from animax.models.plugin import HealthStatus, PluginCategory, PluginInfo, PluginSource


class DummyMetadataProvider(BasePlugin):
    def __init__(
        self,
        name: str = "dummy",
        version: str = "1.0.0",
        priority: int = 100,
        api_version: str = "1.0.0",
    ) -> None:
        self._name = name
        self._version = version
        self._priority = priority
        self._api_version = api_version

    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name=self._name,
            version=self._version,
            description="A dummy metadata plugin for tests.",
            category=PluginCategory.METADATA,
            version="1.0.0",
            author="animax",
            api_version=self._api_version,
            priority=self._priority,
        )

    async def search(self, query: str) -> list[SearchResult]:
        return []

    async def get_details(self, external_id: str) -> MediaItem:
        return MediaItem(id=external_id, title="Dummy")

    async def get_episodes(self, external_id: str) -> list[Any]:
        return []

    async def check_health(self) -> bool:
        return True

    @property
    def capabilities(self) -> set[str]:
        return {"search", "details", "episodes"}


class NotAPlugin:
    """Declares metadata but doesn't implement any plugin interface."""

    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="broken",
            description="",
            category=PluginCategory.METADATA,
            version="1.0.0",
            author="animax",
            api_version="1.0.0"
        )


def make_manager(**kwargs: object) -> PluginManager:
    """A PluginManager wired to a private EventBus, so unit tests never
    touch the process-wide default_bus."""
    kwargs.setdefault("plugin_api_version", "1.0.0")
    kwargs.setdefault("event_bus", EventBus())
    from animax.core.provider_registry import ProviderRegistry
    kwargs.setdefault("provider_registry", ProviderRegistry())
    return PluginManager(**kwargs)  # type: ignore[arg-type]


async def test_register_valid_plugin_adds_to_registry() -> None:
    manager = make_manager()
    warnings: list[str] = []

    await manager._register(DummyMetadataProvider(), PluginSource.BUILTIN, warnings)

    record = manager.get("dummy")
    assert record is not None
    assert record.enabled is True
    assert record.health == HealthStatus.UNKNOWN
    assert warnings == []


async def test_register_rejects_wrong_interface() -> None:
    manager = make_manager()
    warnings: list[str] = []

    # Deliberately not a BasePlugin — exercises the runtime isinstance() check.
    await manager._register(NotAPlugin(), PluginSource.BUILTIN, warnings)  # type: ignore[arg-type]

    assert manager.get("broken") is None
    assert len(warnings) == 1


async def test_register_rejects_incompatible_api_version() -> None:
    manager = make_manager(plugin_api_version="2.0.0")
    warnings: list[str] = []

    await manager._register(
        DummyMetadataProvider(api_version="1.0.0"), PluginSource.BUILTIN, warnings
    )

    assert manager.get("dummy") is None
    assert len(warnings) == 1


async def test_collision_later_source_wins_and_loser_is_shadowed() -> None:
    manager = make_manager()
    warnings: list[str] = []

    builtin = DummyMetadataProvider(name="dup", version="1.0.0")
    user = DummyMetadataProvider(name="dup", version="2.0.0")
    await manager._register(builtin, PluginSource.BUILTIN, warnings)
    await manager._register(user, PluginSource.USER, warnings)

    record = manager.get("dup")
    assert record is not None
    assert record.source == PluginSource.USER
    assert record.info.version == "2.0.0"
    assert len(warnings) == 1


async def test_enabled_sorted_by_priority() -> None:
    manager = make_manager()
    warnings: list[str] = []

    await manager._register(
        DummyMetadataProvider(name="low", priority=50), PluginSource.BUILTIN, warnings
    )
    await manager._register(
        DummyMetadataProvider(name="high", priority=10), PluginSource.BUILTIN, warnings
    )

    ordered = manager.enabled(category="metadata")

    assert [r.info.name for r in ordered] == ["high", "low"]


async def test_enable_disable_roundtrip() -> None:
    manager = make_manager()
    warnings: list[str] = []
    await manager._register(DummyMetadataProvider(), PluginSource.BUILTIN, warnings)

    manager.disable("dummy")
    assert manager.enabled() == []

    manager.enable("dummy")
    assert len(manager.enabled()) == 1


async def test_health_check_all_sets_health() -> None:
    manager = make_manager()
    warnings: list[str] = []
    await manager._register(DummyMetadataProvider(), PluginSource.BUILTIN, warnings)

    await manager.health_check_all()

    record = manager.get("dummy")
    assert record is not None
    assert record.health == HealthStatus.HEALTHY


async def test_register_publishes_provider_loaded_event() -> None:
    bus = EventBus()
    received: list[ProviderLoadedEvent] = []

    async def handler(event: ProviderLoadedEvent) -> None:
        received.append(event)

    bus.subscribe(ProviderLoadedEvent, handler)
    manager = make_manager(event_bus=bus)
    warnings: list[str] = []

    await manager._register(DummyMetadataProvider(), PluginSource.BUILTIN, warnings)

    assert len(received) == 1
    assert received[0].record.info.name == "dummy"


async def test_register_publishes_provider_rejected_event_on_validation_failure() -> None:
    bus = EventBus()
    received: list[ProviderRejectedEvent] = []

    async def handler(event: ProviderRejectedEvent) -> None:
        received.append(event)

    bus.subscribe(ProviderRejectedEvent, handler)
    manager = make_manager(plugin_api_event_bus=bus)
    warnings: list[str] = []

    await manager._register(
        DummyMetadataProvider(api_version="1.0.0"), PluginSource.BUILTIN, warnings
    )

    assert len(received) == 1
    assert received[0].plugin_name == "dummy"


async def test_health_check_all_publishes_health_changed_event() -> None:
    bus = EventBus()
    received: list[ProviderHealthChangedEvent] = []

    async def handler(event: ProviderHealthChangedEvent) -> None:
        received.append(event)

    bus.subscribe(ProviderHealthChangedEvent, handler)
    manager = make_manager(event_bus=bus)
    warnings: list[str] = []
    await manager._register(DummyMetadataProvider(), PluginSource.BUILTIN, warnings)

    await manager.health_check_all()

    assert len(received) == 1
    assert received[0].previous_health == HealthStatus.UNKNOWN
    assert received[0].record.health == HealthStatus.HEALTHY


async def test_load_all_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = make_manager()
    calls = 0

    def fake_discover_builtin(package_name: str) -> list[BasePlugin]:
        nonlocal calls
        calls += 1
        return [DummyMetadataProvider()]

    monkeypatch.setattr(manager, "_discover_builtin", fake_discover_builtin)

    first = await manager.load_all()
    second = await manager.load_all()

    assert calls == 1
    assert first == second == []
    assert len(manager.registry) == 1


async def test_reload_forces_fresh_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = make_manager()
    calls = 0

    def fake_discover_builtin(package_name: str) -> list[BasePlugin]:
        nonlocal calls
        calls += 1
        return [DummyMetadataProvider()]

    monkeypatch.setattr(manager, "_discover_builtin", fake_discover_builtin)

    await manager.load_all()
    await manager.reload()

    assert calls == 2
    assert len(manager.registry) == 1

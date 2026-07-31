from __future__ import annotations

from animax.core.interfaces.metadata import MetadataPlugin
from animax.core.plugin_manager import PluginManager
from animax.models.media import MediaItem, SearchResult
from animax.models.plugin import HealthStatus, PluginCategory, PluginInfo, PluginSource


class DummyMetadataPlugin(MetadataPlugin):
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
            author="test",
            description="A dummy metadata plugin for tests.",
            category=PluginCategory.METADATA,
            api_version=self._api_version,
            priority=self._priority,
        )

    async def search(self, query: str) -> list[SearchResult]:
        return []

    async def get_details(self, external_id: str) -> MediaItem:
        return MediaItem(id=external_id, title="Dummy")


class NotAPlugin:
    """Declares metadata but doesn't implement any plugin interface."""

    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="broken",
            version="1.0.0",
            author="test",
            description="",
            category=PluginCategory.METADATA,
            api_version="1.0.0",
        )


def test_register_valid_plugin_adds_to_registry() -> None:
    manager = PluginManager(plugin_api_version="1.0.0")
    warnings: list[str] = []

    manager._register(DummyMetadataPlugin(), PluginSource.BUILTIN, warnings)

    record = manager.get("dummy")
    assert record is not None
    assert record.enabled is True
    assert record.health == HealthStatus.UNKNOWN
    assert warnings == []


def test_register_rejects_wrong_interface() -> None:
    manager = PluginManager(plugin_api_version="1.0.0")
    warnings: list[str] = []

    # Deliberately not a BasePlugin — exercises the runtime isinstance() check.
    manager._register(NotAPlugin(), PluginSource.BUILTIN, warnings)  # type: ignore[arg-type]

    assert manager.get("broken") is None
    assert len(warnings) == 1


def test_register_rejects_incompatible_api_version() -> None:
    manager = PluginManager(plugin_api_version="2.0.0")
    warnings: list[str] = []

    manager._register(DummyMetadataPlugin(api_version="1.0.0"), PluginSource.BUILTIN, warnings)

    assert manager.get("dummy") is None
    assert len(warnings) == 1


def test_collision_later_source_wins_and_loser_is_shadowed() -> None:
    manager = PluginManager(plugin_api_version="1.0.0")
    warnings: list[str] = []

    builtin = DummyMetadataPlugin(name="dup", version="1.0.0")
    user = DummyMetadataPlugin(name="dup", version="2.0.0")
    manager._register(builtin, PluginSource.BUILTIN, warnings)
    manager._register(user, PluginSource.USER, warnings)

    record = manager.get("dup")
    assert record is not None
    assert record.source == PluginSource.USER
    assert record.info.version == "2.0.0"
    assert len(warnings) == 1


def test_enabled_sorted_by_priority() -> None:
    manager = PluginManager(plugin_api_version="1.0.0")
    warnings: list[str] = []

    manager._register(DummyMetadataPlugin(name="low", priority=50), PluginSource.BUILTIN, warnings)
    manager._register(DummyMetadataPlugin(name="high", priority=10), PluginSource.BUILTIN, warnings)

    ordered = manager.enabled(category="metadata")

    assert [r.info.name for r in ordered] == ["high", "low"]


def test_enable_disable_roundtrip() -> None:
    manager = PluginManager(plugin_api_version="1.0.0")
    warnings: list[str] = []
    manager._register(DummyMetadataPlugin(), PluginSource.BUILTIN, warnings)

    manager.disable("dummy")
    assert manager.enabled() == []

    manager.enable("dummy")
    assert len(manager.enabled()) == 1


async def test_health_check_all_sets_health() -> None:
    manager = PluginManager(plugin_api_version="1.0.0")
    warnings: list[str] = []
    manager._register(DummyMetadataPlugin(), PluginSource.BUILTIN, warnings)

    await manager.health_check_all()

    record = manager.get("dummy")
    assert record is not None
    assert record.health == HealthStatus.HEALTHY

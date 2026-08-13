"""Business logic around plugin discovery, wrapping core.plugin_manager."""

from __future__ import annotations

from animax.config.paths import user_plugin_dir
from animax.core.constants import PLUGIN_API_VERSION
from animax.core.plugin_manager import PluginManager
from animax.core.provider_registry import ProviderRegistry
from animax.models.plugin import PluginRecord

_manager_singleton: PluginManager | None = None
_registry_singleton: ProviderRegistry | None = None


def get_provider_registry() -> ProviderRegistry:
    global _registry_singleton
    if _registry_singleton is None:
        _registry_singleton = ProviderRegistry()
    return _registry_singleton


def get_plugin_manager() -> PluginManager:
    global _manager_singleton
    if _manager_singleton is None:
        _manager_singleton = PluginManager(
            plugin_api_version=PLUGIN_API_VERSION,
            provider_registry=get_provider_registry(),
            user_plugin_dir=user_plugin_dir()
        )
    return _manager_singleton

def reset_plugin_manager() -> None:
    global _manager_singleton
    global _registry_singleton
    _manager_singleton = None
    _registry_singleton = None

async def discover_plugins() -> tuple[list[PluginRecord], list[str]]:
    """Load all plugins (built-in -> user -> entry-point) and return them, priority-ordered."""
    manager = get_plugin_manager()
    warnings = await manager.load_all()
    records = sorted(
        manager.registry.values(), key=lambda r: (r.info.category.value, r.info.priority)
    )
    return records, warnings

"""Plugin discovery, loading, validation, and lifecycle management.

Load order (see docs/Plugin-System.md):

    1. Built-in plugins bundled under ``animax.plugins.*``.
    2. User plugins, directory-scanned from the user plugin directory.
    3. Entry-point plugins, pip-installed and registered under the
       ``animax.plugins`` entry-point group.

A later source wins on a name collision. The overridden plugin is never
silently dropped: it stays in the registry, disabled, with
``shadowed_by`` set to the name of the plugin that won — visible via
``anime plugins``. A plugin that fails to import, instantiate, or validate
is logged and skipped; it can never take down the rest of the application
(error isolation).
"""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import inspect
import logging
import pkgutil
from pathlib import Path
from types import ModuleType

from animax.core.constants import PLUGIN_ENTRY_POINT_GROUP
from animax.core.errors import PluginValidationError, PluginVersionMismatchError
from animax.core.events import default_bus, EventBus
from animax.core.events.plugin_events import (
    ProviderLoadedEvent,
    ProviderRejectedEvent,
    ProviderHealthChangedEvent,
)
from animax.core.interfaces import CATEGORY_INTERFACES, BasePlugin
from animax.core.versioning import is_compatible
from animax.models.plugin import HealthStatus, PluginInfo, PluginRecord, PluginSource

logger = logging.getLogger(__name__)


class PluginManager:
    """Discovers, validates, and tracks the lifecycle of all plugins."""

    def __init__(
        self,
        *,
        plugin_api_version: str,
        user_plugin_dir: Path | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._plugin_api_version = plugin_api_version
        self._user_plugin_dir = user_plugin_dir
        self._registry: dict[str, PluginRecord] = {}
        self._bus = event_bus or default_bus

    @property
    def registry(self) -> dict[str, PluginRecord]:
        return dict(self._registry)

    def get(self, name: str) -> PluginRecord | None:
        return self._registry.get(name)

    def enabled(self, category: str | None = None) -> list[PluginRecord]:
        """Enabled plugins, priority-ordered (lower number = higher priority)."""
        records = [r for r in self._registry.values() if r.enabled]
        if category is not None:
            records = [r for r in records if r.info.category.value == category]
        return sorted(records, key=lambda r: r.info.priority)

    async def load_all(self, *, builtin_package: str = "animax.plugins") -> list[str]:
        """Discover and load plugins from all sources in load order.

        Returns a list of human-readable warnings (rejected plugins,
        collisions) for the caller to surface, e.g. via ``anime plugins``.
        """
        if self._registry:
            return []
            
        warnings: list[str] = []
        for instance in self._discover_builtin(builtin_package):
            await self._register(instance, PluginSource.BUILTIN, warnings)
        if self._user_plugin_dir is not None:
            for instance in self._discover_user_dir(self._user_plugin_dir):
                await self._register(instance, PluginSource.USER, warnings)
        for instance in self._discover_entry_points():
            await self._register(instance, PluginSource.ENTRY_POINT, warnings)
        return warnings

    async def reload(self) -> None:
        self._registry.clear()
        await self.load_all()

    # -- discovery ---------------------------------------------------

    def _discover_builtin(self, package_name: str) -> list[BasePlugin]:
        instances: list[BasePlugin] = []
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            return instances
        if not hasattr(package, "__path__"):
            return instances
        for _finder, module_name, is_pkg in pkgutil.walk_packages(
            package.__path__, prefix=f"{package_name}."
        ):
            if is_pkg:
                continue
            instance = self._safe_load_module(module_name)
            if instance is not None:
                instances.append(instance)
        return instances

    def _discover_user_dir(self, directory: Path) -> list[BasePlugin]:
        instances: list[BasePlugin] = []
        if not directory.is_dir():
            return instances
        for path in sorted(directory.glob("*.py")):
            if path.name.startswith("_"):
                continue
            instance = self._safe_load_path(path)
            if instance is not None:
                instances.append(instance)
        return instances

    def _discover_entry_points(self) -> list[BasePlugin]:
        instances: list[BasePlugin] = []
        for ep in importlib.metadata.entry_points(group=PLUGIN_ENTRY_POINT_GROUP):
            try:
                plugin_cls = ep.load()
                instance = self._instantiate(plugin_cls)
            except Exception:
                logger.exception("Failed to load entry-point plugin %r", ep.name)
                continue
            if instance is not None:
                instances.append(instance)
        return instances

    # -- import helpers ------------------------------------------------

    def _safe_load_module(self, module_name: str) -> BasePlugin | None:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            logger.exception("Failed to import plugin module %r", module_name)
            return None
        return self._find_plugin_in_module(module)

    def _safe_load_path(self, path: Path) -> BasePlugin | None:
        module_name = f"animax._user_plugin_{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not build an import spec for {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception:
            logger.exception("Failed to import user plugin %s", path)
            return None
        return self._find_plugin_in_module(module)

    def _find_plugin_in_module(self, module: ModuleType) -> BasePlugin | None:
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, BasePlugin)
                and obj is not BasePlugin
                and obj.__module__ == module.__name__
            ):
                return self._instantiate(obj)
        return None

    def _instantiate(self, plugin_cls: type[BasePlugin]) -> BasePlugin | None:
        try:
            return plugin_cls()
        except Exception:
            logger.exception("Failed to instantiate plugin class %r", plugin_cls)
            return None

    # -- registration --------------------------------------------------

    async def _register(self, instance: BasePlugin, source: PluginSource, warnings: list[str]) -> None:
        try:
            info = instance.info
        except Exception as exc:
            logger.exception("Plugin %r raised while reading .info", instance)
            warnings.append(f"{instance!r}: failed to read plugin metadata ({exc})")
            return

        try:
            self._validate(instance, info)
        except (PluginValidationError, PluginVersionMismatchError) as exc:
            logger.warning("Rejected plugin %r: %s", info.name, exc)
            warnings.append(f"{info.name}: {exc}")
            await self._bus.publish(ProviderRejectedEvent(plugin_name=info.name, reason=str(exc)))
            return

        existing = self._registry.get(info.name)
        if existing is not None and existing.enabled:
            # Later source wins per load order; the loser is disabled, not dropped.
            existing.enabled = False
            existing.shadowed_by = info.name
            msg = (
                f"Plugin name collision: {info.name!r} from {source.value} "
                f"overrides {existing.source.value} plugin of the same name"
            )
            logger.warning(msg)
            warnings.append(msg)

        record = PluginRecord(
            info=info,
            instance=instance,
            source=source,
            enabled=True,
            health=HealthStatus.UNKNOWN,
        )
        self._registry[info.name] = record
        await self._bus.publish(ProviderLoadedEvent(record=record))

    def _validate(self, instance: BasePlugin, info: PluginInfo) -> None:
        interface = CATEGORY_INTERFACES.get(info.category.value)
        if interface is None or not isinstance(instance, interface):
            raise PluginValidationError(
                f"{info.name!r} declares category {info.category!r} but does not "
                f"implement the corresponding interface"
            )
        if not is_compatible(self._plugin_api_version, info.api_version):
            raise PluginVersionMismatchError(
                f"{info.name!r} targets plugin API {info.api_version}, "
                f"incompatible with this app's {self._plugin_api_version}"
            )

    # -- lifecycle -------------------------------------------------------

    def enable(self, name: str) -> None:
        self._require(name).enabled = True

    def disable(self, name: str) -> None:
        self._require(name).enabled = False

    async def health_check_all(self) -> None:
        for name, record in self._registry.items():
            if not record.enabled:
                record.health = HealthStatus.DISABLED
                continue
            prev_health = record.health
            try:
                is_healthy = await record.instance.check_health()
                record.health = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
            except Exception as exc:
                record.health = HealthStatus.UNHEALTHY
                record.health_detail = str(exc)
                logger.exception("Health check failed for plugin %r", name)
            
            if record.health != prev_health:
                await self._bus.publish(
                    ProviderHealthChangedEvent(record=record, previous_health=prev_health)
                )

    def _require(self, name: str) -> PluginRecord:
        record = self._registry.get(name)
        if record is None:
            raise KeyError(f"No plugin registered as {name!r}")
        return record

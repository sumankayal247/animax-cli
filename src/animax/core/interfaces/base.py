"""Base plugin interface. Every plugin category's ABC inherits from this.

The core application (plugin_manager, services) only ever talks to plugins
through these interfaces — never through a concrete provider class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from animax.models.plugin import HealthStatus, PluginInfo


class BasePlugin(ABC):
    """Common contract every Animax-Cli plugin must implement."""

    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """Static metadata this plugin declares about itself."""
        raise NotImplementedError

    async def setup(self) -> None:
        """Called once after the plugin is loaded and validated, before first use.

        Default is a no-op; override to open clients, warm caches, etc.
        """
        return None

    async def teardown(self) -> None:
        """Called on shutdown or when the plugin is disabled at runtime.

        Default is a no-op; override to release resources.
        """
        return None

    async def check_health(self) -> bool:
        """Report this plugin's current health.

        Default assumes healthy; plugins that depend on external services
        (an API, a player binary) should override this with a real check.
        """
        return True

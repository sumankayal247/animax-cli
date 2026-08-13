"""Shared plugin metadata and registry models.

``PluginInfo`` is the static metadata a plugin author declares about their
plugin. ``PluginRecord`` is the runtime wrapper the plugin manager builds
around a loaded plugin instance (source, enabled state, health, etc.).
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from animax.core.interfaces.base import BasePlugin


class PluginCategory(StrEnum):
    METADATA = "metadata"
    DOWNLOAD = "download"
    STREAMING = "streaming"
    PLAYER = "player"
    NOTIFICATION = "notification"
    AUTHENTICATION = "authentication"
    SEARCH = "search"
    SOURCE = "source"


class PluginSource(StrEnum):
    BUILTIN = "builtin"
    USER = "user"
    ENTRY_POINT = "entry_point"


class HealthStatus(StrEnum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"


class ProviderCapabilities(BaseModel):
    """Structured capabilities advertised by a provider."""

    model_config = ConfigDict(frozen=True)

    search: bool = False
    metadata: bool = False
    episodes: bool = False
    stream: bool = False
    download: bool = False
    magnet: bool = False


class PluginInfo(BaseModel):
    """Static metadata a plugin declares about itself."""

    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    author: str
    description: str
    category: PluginCategory
    api_version: str
    priority: int = 100
    capabilities: ProviderCapabilities = Field(default_factory=ProviderCapabilities)


class PluginRecord(BaseModel):
    """Runtime registry entry combining declared metadata with load state."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    info: PluginInfo
    instance: Any = Field(repr=False)  # BasePlugin, kept as Any to avoid pydantic ABC coercion
    source: PluginSource
    enabled: bool = True
    health: HealthStatus = HealthStatus.UNKNOWN
    health_detail: str | None = None
    shadowed_by: str | None = None
    """Set to another plugin's name when this one lost a load-order collision."""

    @property
    def plugin(self) -> BasePlugin:
        return cast("BasePlugin", self.instance)

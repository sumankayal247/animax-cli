"""Shared provider metadata and registry models."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from animax.core.interfaces.provider import BaseProvider


class ProviderCategory(StrEnum):
    METADATA = "metadata"
    DOWNLOAD = "download"
    STREAMING = "streaming"
    PLAYER = "player"
    SEARCH = "search"
    SOURCE = "source"


class ProviderCapabilities(BaseModel):
    """Structured capabilities advertised by a provider."""
    model_config = ConfigDict(frozen=True)

    search: bool = False
    metadata: bool = False
    episodes: bool = False
    stream: bool = False
    download: bool = False
    magnet: bool = False


class HealthStatus(StrEnum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"


class ProviderInfo(BaseModel):
    """Static metadata a provider declares about itself."""
    model_config = ConfigDict(frozen=True)

    name: str
    description: str
    category: ProviderCategory
    priority: int = 100
    capabilities: ProviderCapabilities = Field(default_factory=ProviderCapabilities)


class ProviderRecord(BaseModel):
    """Runtime registry entry for a Provider."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    info: ProviderInfo
    instance: Any = Field(repr=False)  # BaseProvider
    plugin_name: str
    enabled: bool = True
    health: HealthStatus = HealthStatus.UNKNOWN
    health_detail: str | None = None
    shadowed_by: str | None = None

    @property
    def provider(self) -> BaseProvider:
        return cast("BaseProvider", self.instance)

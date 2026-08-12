"""Typed events published around the plugin lifecycle.

Published by core.plugin_manager.PluginManager — see its docstring for
exactly when each fires.
"""

from __future__ import annotations

from dataclasses import dataclass

from animax.core.events.event import Event
from animax.models.plugin import HealthStatus, PluginRecord


@dataclass(frozen=True, slots=True)
class ProviderLoadedEvent(Event):
    """A plugin was discovered, passed validation, and was registered."""

    record: PluginRecord


@dataclass(frozen=True, slots=True)
class ProviderRejectedEvent(Event):
    """A discovered plugin failed validation (or raised while loading) and was skipped.

    Named "rejected" rather than "failed": nothing crashed — validation
    simply declined to register it. See PluginManager._validate.
    """

    plugin_name: str
    reason: str


@dataclass(frozen=True, slots=True)
class ProviderHealthChangedEvent(Event):
    """A plugin's health status changed, per PluginManager.health_check_all()."""

    record: PluginRecord
    previous_health: HealthStatus

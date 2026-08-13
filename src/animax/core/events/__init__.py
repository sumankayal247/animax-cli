"""Minimal async event bus for decoupling subsystems."""

from animax.core.events.bus import EventBus, EventHandler, default_bus
from animax.core.events.event import Event
from animax.core.events.plugin_events import (
    ProviderHealthChangedEvent,
    ProviderLoadedEvent,
    ProviderRejectedEvent,
)

__all__ = ["EventBus", "EventHandler", "default_bus", "Event", "ProviderHealthChangedEvent", "ProviderLoadedEvent", "ProviderRejectedEvent"]

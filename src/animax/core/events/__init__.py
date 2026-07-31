"""Minimal async event bus for decoupling subsystems."""

from animax.core.events.bus import EventBus, EventHandler, default_bus

__all__ = ["EventBus", "EventHandler", "default_bus"]

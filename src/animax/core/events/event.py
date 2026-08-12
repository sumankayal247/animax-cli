"""Base class every event published on the bus must inherit from."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Event:
    """Marker base class for typed events. Subclasses are plain frozen dataclasses."""

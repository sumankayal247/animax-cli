"""A minimal async in-process event bus.

Used to decouple subsystems (e.g. the download engine publishing progress
events that the UI layer subscribes to) without giving them direct
references to each other. Handlers are plain async callables; a failing
handler is logged and isolated so it can never break the publisher or
other subscribers — same error-isolation principle as the plugin system.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)

EventHandler = Callable[[Any], Awaitable[None]]


class EventBus:
    """Simple publish/subscribe event bus keyed by event type name."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_name)
        if handlers and handler in handlers:
            handlers.remove(handler)

    async def publish(self, event_name: str, payload: Any = None) -> None:
        for handler in list(self._handlers.get(event_name, ())):
            try:
                await handler(payload)
            except Exception:
                logger.exception("Event handler for %r raised an exception", event_name)


#: Process-wide default bus. Subsystems may also construct a private
#: EventBus() for testing/isolation instead of using this singleton.
default_bus = EventBus()

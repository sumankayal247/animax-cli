"""A minimal async in-process event bus.

Used to decouple subsystems (e.g. the download engine publishing progress
events that the UI layer subscribes to) without giving them direct
references to each other. Handlers are plain async callables; a failing
handler is logged and isolated so it can never break the publisher or
other subscribers — same error-isolation principle as the plugin system.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

TEvent = TypeVar("TEvent")
EventHandler = Callable[[TEvent], Awaitable[None]]


class EventBus:
    """Simple publish/subscribe event bus keyed by event type."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler[Any]]] = defaultdict(list)

    def subscribe(self, event_type: type[TEvent], handler: EventHandler[TEvent]) -> None:
        self._handlers[event_type].append(handler) 

    def unsubscribe(self, event_type: type[TEvent], handler: EventHandler[TEvent]) -> None:
        handlers = self._handlers.get(event_type)
        if handlers and handler in handlers:
            handlers.remove(handler) 

    async def publish(self, event: Any) -> None:
        event_type = type(event)
        handlers = list(self._handlers.get(event_type, ()))
        
        async def _run_handler(h: EventHandler[Any]) -> None:
            try:
                await h(event)
            except Exception:
                logger.exception("Event handler for %r raised an exception", event_type.__name__)

        if handlers:
            await asyncio.gather(*(_run_handler(h) for h in handlers))


#: Process-wide default bus. Subsystems may also construct a private
#: EventBus() for testing/isolation instead of using this singleton.
default_bus = EventBus()

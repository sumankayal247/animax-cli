from __future__ import annotations

from dataclasses import dataclass

from animax.core.events import Event, EventBus


@dataclass(frozen=True, slots=True)
class SampleEvent(Event):
    value: int


@dataclass(frozen=True, slots=True)
class OtherEvent(Event):
    pass


async def test_subscriber_receives_published_event() -> None:
    bus = EventBus()
    received: list[SampleEvent] = []

    async def handler(event: SampleEvent) -> None:
        received.append(event)

    bus.subscribe(SampleEvent, handler)
    await bus.publish(SampleEvent(value=42))

    assert received == [SampleEvent(value=42)]


async def test_subscriber_only_receives_its_own_event_type() -> None:
    bus = EventBus()
    received: list[SampleEvent] = []

    async def handler(event: SampleEvent) -> None:
        received.append(event)

    bus.subscribe(SampleEvent, handler)
    await bus.publish(OtherEvent())

    assert received == []


async def test_unsubscribe_stops_delivery() -> None:
    bus = EventBus()
    received: list[SampleEvent] = []

    async def handler(event: SampleEvent) -> None:
        received.append(event)

    bus.subscribe(SampleEvent, handler)
    bus.unsubscribe(SampleEvent, handler)
    await bus.publish(SampleEvent(value=1))

    assert received == []


async def test_failing_handler_does_not_break_other_handlers() -> None:
    bus = EventBus()
    received: list[SampleEvent] = []

    async def failing_handler(event: SampleEvent) -> None:
        raise RuntimeError("boom")

    async def good_handler(event: SampleEvent) -> None:
        received.append(event)

    bus.subscribe(SampleEvent, failing_handler)
    bus.subscribe(SampleEvent, good_handler)

    await bus.publish(SampleEvent(value=7))

    assert received == [SampleEvent(value=7)]


async def test_multiple_subscribers_all_receive_event() -> None:
    bus = EventBus()
    counts = {"a": 0, "b": 0}

    async def handler_a(event: SampleEvent) -> None:
        counts["a"] += 1

    async def handler_b(event: SampleEvent) -> None:
        counts["b"] += 1

    bus.subscribe(SampleEvent, handler_a)
    bus.subscribe(SampleEvent, handler_b)
    await bus.publish(SampleEvent(value=1))

    assert counts == {"a": 1, "b": 1}

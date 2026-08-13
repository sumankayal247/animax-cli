"""Provider registry for managing content-supplying providers."""

from __future__ import annotations

import logging

from animax.models.provider import ProviderRecord

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Tracks and manages all registered content providers."""

    def __init__(self) -> None:
        self._registry: dict[str, ProviderRecord] = {}

    @property
    def registry(self) -> dict[str, ProviderRecord]:
        return dict(self._registry)

    def get(self, name: str) -> ProviderRecord | None:
        return self._registry.get(name)

    def enabled(self, category: str | None = None) -> list[ProviderRecord]:
        """Enabled providers, priority-ordered."""
        records = [r for r in self._registry.values() if r.enabled]
        if category is not None:
            records = [r for r in records if r.info.category.value == category]
        return sorted(records, key=lambda r: r.info.priority)

    def register(self, record: ProviderRecord) -> None:
        existing = self._registry.get(record.info.name)
        if existing is not None and existing.enabled:
            existing.enabled = False
            existing.shadowed_by = record.info.name
            logger.warning(
                "Provider name collision: %r overrides existing provider of the same name",
                record.info.name,
            )
        self._registry[record.info.name] = record

    def clear(self) -> None:
        self._registry.clear()

    def enable(self, name: str) -> None:
        self._require(name).enabled = True

    def disable(self, name: str) -> None:
        self._require(name).enabled = False

    def _require(self, name: str) -> ProviderRecord:
        record = self._registry.get(name)
        if record is None:
            raise KeyError(f"No provider registered as {name!r}")
        return record

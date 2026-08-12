"""Cache orchestration logic."""

from __future__ import annotations

from animax.cache.store import Cache


def get_cache(namespace: str) -> Cache:
    return Cache(namespace)

from __future__ import annotations

import time
from pathlib import Path

from animax.cache.store import Cache


def test_cache_miss_hit_stats(tmp_path: Path) -> None:
    c = Cache("test", directory=tmp_path)
    assert c.get("nonexistent") is None
    assert c.stats.misses == 1
    assert c.stats.hits == 0

    c.set("exists", "value")
    assert c.get("exists") == "value"
    assert c.stats.misses == 1
    assert c.stats.hits == 1


def test_cache_max_size_eviction(tmp_path: Path) -> None:
    # Setting a max size of 50 bytes. Each file will be around 40-50 bytes.
    c = Cache("test_size", directory=tmp_path, max_size_bytes=80)

    # Store first item
    c.set("item1", "A" * 10)  # Takes ~50 bytes
    time.sleep(0.01)  # Ensure mtime differs

    # Store second item
    c.set("item2", "B" * 10)  # Takes ~50 bytes, total > 80, evicts item1

    assert c.get("item1") is None
    assert c.get("item2") == "B" * 10
    assert c.stats.evictions == 1


def test_set_and_get_roundtrip(tmp_path: Path) -> None:
    cache = Cache("test-ns", directory=tmp_path)
    cache.set("key", {"a": 1})
    assert cache.get("key") == {"a": 1}


def test_get_missing_key_returns_none(tmp_path: Path) -> None:
    cache = Cache("test-ns", directory=tmp_path)
    assert cache.get("missing") is None


def test_expired_entry_returns_none(tmp_path: Path) -> None:
    cache = Cache("test-ns", directory=tmp_path)
    cache.set("key", "value", ttl_seconds=-1)
    assert cache.get("key") is None


def test_clear_removes_all_entries(tmp_path: Path) -> None:
    cache = Cache("test-ns", directory=tmp_path)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.clear()
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_cleanup_expired_counts_removed(tmp_path: Path) -> None:
    cache = Cache("test-ns", directory=tmp_path)
    cache.set("stale", 1, ttl_seconds=-1)
    cache.set("fresh", 2, ttl_seconds=3600)
    removed = cache.cleanup_expired()
    assert removed == 1
    assert cache.get("fresh") == 2

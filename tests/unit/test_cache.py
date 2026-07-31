from __future__ import annotations

from pathlib import Path

from animax.cache.store import Cache


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

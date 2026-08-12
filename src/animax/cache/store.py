"""A simple namespaced, TTL-based on-disk cache backed by JSON files.

Deliberately provider-agnostic: metadata plugins, search aggregation, and
config all get their own ``Cache(namespace=...)`` instance rather than
sharing state, so one plugin's cache can be cleared without affecting
another's.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from animax.config.paths import cache_dir


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0


class Cache:
    """Namespaced key/value cache with per-entry expiration."""

    def __init__(
        self,
        namespace: str,
        *,
        directory: Path | None = None,
        default_ttl_seconds: int = 86_400,
        max_size_bytes: int | None = None,
    ) -> None:
        self._dir = (directory or cache_dir()) / namespace
        self._default_ttl = default_ttl_seconds
        self._max_size_bytes = max_size_bytes
        self.stats = CacheStats()

    def _path_for(self, key: str) -> Path:
        safe_key = key.replace("/", "_")
        return self._dir / f"{safe_key}.json"

    def get(self, key: str) -> Any | None:
        path = self._path_for(key)
        if not path.exists():
            self.stats.misses += 1
            return None
        try:
            payload = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            self.stats.misses += 1
            return None
        expires_at = payload.get("expires_at")
        if expires_at is not None and expires_at < time.time():
            path.unlink(missing_ok=True)
            self.stats.misses += 1
            return None
        self.stats.hits += 1
        return payload.get("value")

    def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        ttl = self._default_ttl if ttl_seconds is None else ttl_seconds
        payload = {"value": value, "expires_at": time.time() + ttl}
        self._path_for(key).write_text(json.dumps(payload))
        
        if self._max_size_bytes is not None:
            self._enforce_size_limit()

    def _enforce_size_limit(self) -> None:
        if not self._dir.exists():
            return
        files = list(self._dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)
        if total_size <= self._max_size_bytes:
            return
            
        files.sort(key=lambda f: f.stat().st_mtime)
        for f in files:
            size = f.stat().st_size
            f.unlink(missing_ok=True)
            self.stats.evictions += 1
            total_size -= size
            if total_size <= self._max_size_bytes:
                break

    def clear(self) -> None:
        if not self._dir.exists():
            return
        for path in self._dir.glob("*.json"):
            path.unlink(missing_ok=True)

    def cleanup_expired(self) -> int:
        if not self._dir.exists():
            return 0
        removed = 0
        now = time.time()
        for path in self._dir.glob("*.json"):
            try:
                payload = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                path.unlink(missing_ok=True)
                removed += 1
                continue
            expires_at = payload.get("expires_at")
            if expires_at is not None and expires_at < now:
                path.unlink(missing_ok=True)
                removed += 1
        return removed

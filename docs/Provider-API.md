# Provider API

The exact method contract each plugin category must implement, beyond the
common `BasePlugin.info` / `.setup()` / `.teardown()` / `.health_check()`.
All models referenced are in `animax.models`.

## MetadataPlugin (`core/interfaces/metadata.py`)

```python
async def search(self, query: str) -> list[SearchResult]: ...
async def get_details(self, external_id: str) -> MediaItem: ...
```

## SearchPlugin (`core/interfaces/search.py`)

```python
async def find(self, item: MediaItem) -> list[SearchResult]: ...
```

## DownloadPlugin (`core/interfaces/download.py`)

```python
async def resolve(self, item: MediaItem, episode: Episode) -> list[ContentSource]: ...
```

## StreamingPlugin (`core/interfaces/streaming.py`)

```python
async def resolve(self, item: MediaItem, episode: Episode) -> list[ContentSource]: ...
```

## PlayerPlugin (`core/interfaces/player.py`)

```python
def is_available(self) -> bool: ...
async def play(self, target: str, *, resume_at_seconds: float | None = None) -> None: ...
```

## NotificationPlugin (`core/interfaces/notification.py`)

```python
async def notify(self, title: str, message: str, *, level: NotificationLevel) -> None: ...
```

## AuthenticationPlugin (`core/interfaces/authentication.py`)

```python
async def is_authenticated(self) -> bool: ...
async def login(self, **credentials: str) -> None: ...
async def logout(self) -> None: ...
```

## Rules

- Never raise a bare exception across the boundary — wrap in
  `core.errors.PluginError` (or a subclass) with a `reason` and, where
  possible, a `fix`.
- Never block the event loop — use `httpx.AsyncClient`, not `requests` or
  a synchronous HTTP call.
- Return only `animax.models.*` types. Provider-native JSON/HTML shapes
  must never leak outside the plugin module that parses them.

This document grows as Phase 4/5 land real plugins and the interfaces
inevitably need small additions — keep it in sync with `core/interfaces/`.

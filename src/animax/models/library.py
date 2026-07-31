"""Domain models for the local library: history, favorites, resume state."""

from __future__ import annotations

from pydantic import BaseModel


class LibraryEntry(BaseModel):
    """A media item the user has interacted with (watched, downloaded, favorited)."""

    media_id: str
    title: str
    is_favorite: bool = False
    last_episode: float | None = None
    resume_position_seconds: float | None = None
    last_played_at: float | None = None
    """Unix timestamp of last playback, if any."""
    plugin_used: str | None = None


class HistoryEntry(BaseModel):
    """A single watch or download event, for the history log."""

    media_id: str
    title: str
    episode: float
    event: str
    """e.g. "played", "downloaded"."""
    occurred_at: float
    plugin_used: str | None = None

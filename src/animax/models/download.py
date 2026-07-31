"""Domain models for downloadable/streamable sources and download tasks."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SourceKind(StrEnum):
    DOWNLOAD = "download"
    STREAM = "stream"


class ContentSource(BaseModel):
    """A single resolved, playable/downloadable source for one episode.

    Produced by download/streaming plugins; consumed by the download engine
    and the player framework.
    """

    url: str
    kind: SourceKind
    quality: str | None = None
    plugin: str
    headers: dict[str, str] = Field(default_factory=dict)
    expires_at: float | None = None
    """Unix timestamp after which ``url`` is no longer valid, if known."""


class DownloadStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DownloadTask(BaseModel):
    """A single item in the download queue."""

    id: str
    media_id: str
    episode: float
    destination: str
    source: ContentSource
    status: DownloadStatus = DownloadStatus.QUEUED
    progress: float = 0.0
    bytes_downloaded: int = 0
    bytes_total: int | None = None
    retries: int = 0
    error: str | None = None

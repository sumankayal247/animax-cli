"""Typed events for the download engine.

Declared now because the DownloadTask model they carry already exists
(models.download) and fixing the contract early costs nothing — but there
is no publisher yet. That lands with the download engine in Phase 5
(download/), consumed by a Rich Live progress view in ui/. See
docs/Architecture.md "Events".
"""

from __future__ import annotations

from dataclasses import dataclass

from animax.core.events.event import Event
from animax.models.download import DownloadTask


@dataclass(frozen=True, slots=True)
class DownloadStartedEvent(Event):
    task: DownloadTask


@dataclass(frozen=True, slots=True)
class DownloadProgressEvent(Event):
    task: DownloadTask


@dataclass(frozen=True, slots=True)
class DownloadCompletedEvent(Event):
    task: DownloadTask


@dataclass(frozen=True, slots=True)
class DownloadFailedEvent(Event):
    task: DownloadTask
    reason: str

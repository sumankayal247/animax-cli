"""Interface for local media player plugins (mpv, VLC, system default, ...)."""

from __future__ import annotations

from abc import abstractmethod

from animax.core.interfaces.provider import BaseProvider


class PlayerProvider(BaseProvider):
    """Launches a local player for a file path or stream URL."""

    @abstractmethod
    def is_available(self) -> bool:
        """True if the underlying player binary/app is installed and usable."""
        raise NotImplementedError

    @abstractmethod
    async def play(self, target: str, *, resume_at_seconds: float | None = None) -> None:
        """Launch playback of a local file path or stream URL."""
        raise NotImplementedError

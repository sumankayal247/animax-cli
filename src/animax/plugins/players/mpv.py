"""MPV media player integration."""

from __future__ import annotations

import asyncio
import logging
import shutil

from animax.core.interfaces.player import PlayerProvider
from animax.models.provider import ProviderCategory, ProviderInfo

logger = logging.getLogger(__name__)

class MPVPlayerProvider(PlayerProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="mpv",
            category=ProviderCategory.PLAYER,
            description="Uses the mpv command-line player.",
            priority=10,
        )

    def is_available(self) -> bool:
        return shutil.which("mpv") is not None

    async def check_health(self) -> bool:
        return self.is_available()

    async def play(self, target: str, *, resume_at_seconds: float | None = None) -> None:
        if not self.is_available():
            raise RuntimeError("mpv binary not found in PATH")
            
        args = ["mpv"]
        if resume_at_seconds is not None and resume_at_seconds > 0:
            args.extend(["--start", str(resume_at_seconds)])
        
        args.append(target)
        
        logger.info(f"Launching mpv: {' '.join(args)}")
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.wait()
        
        if process.returncode != 0:
            logger.error(f"mpv exited with code {process.returncode}")

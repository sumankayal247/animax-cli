"""VLC media player integration."""

from __future__ import annotations

import asyncio
import shutil
import logging
from typing import Any

from animax.core.interfaces.player import PlayerPlugin
from animax.models.plugin import PluginCategory, PluginInfo, HealthStatus

logger = logging.getLogger(__name__)

class VLCPlayerPlugin(PlayerPlugin):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="vlc",
            version="1.0.0",
            category=PluginCategory.PLAYER,
            api_version="1.0.0",
            author="animax",
            description="Uses the VLC media player.",
            priority=20,
        )

    def is_available(self) -> bool:
        return shutil.which("vlc") is not None or shutil.which("cvlc") is not None

    async def check_health(self) -> bool:
        return self.is_available()

    async def play(self, target: str, *, resume_at_seconds: float | None = None) -> None:
        binary = shutil.which("vlc") or shutil.which("cvlc")
        if not binary:
            raise RuntimeError("vlc binary not found in PATH")
            
        args = [binary]
        if resume_at_seconds is not None and resume_at_seconds > 0:
            args.extend(["--start-time", str(resume_at_seconds)])
        
        args.append(target)
        # Prevent VLC from opening a new interface window on macOS/Linux if preferred
        # args.extend(["--play-and-exit"])
        
        logger.info(f"Launching VLC: {' '.join(args)}")
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.wait()
        
        if process.returncode != 0:
            logger.error(f"VLC exited with code {process.returncode}")

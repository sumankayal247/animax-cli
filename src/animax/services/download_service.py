"""Download orchestration logic."""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import httpx

from animax.config.loader import load


class DownloadSession:
    """In-memory session to throttle database updates for highly volatile progress."""

    def __init__(
        self,
        task_id: str,
        db_updater: Callable[[str, int, int], Awaitable[None]],
        checkpoint_interval: float = 5.0,
    ) -> None:
        self.task_id = task_id
        self.db_updater = db_updater
        self.checkpoint_interval = checkpoint_interval
        self.last_checkpoint_time = time.monotonic()
        self.downloaded = 0
        self.total = 0

    async def update_progress(self, downloaded: int, total: int) -> None:
        self.downloaded = downloaded
        self.total = total
        now = time.monotonic()
        if now - self.last_checkpoint_time >= self.checkpoint_interval:
            await self.checkpoint()

    async def checkpoint(self) -> None:
        await self.db_updater(self.task_id, self.downloaded, self.total)
        self.last_checkpoint_time = time.monotonic()

    async def pause(self) -> None:
        await self.checkpoint()

    async def resume(self) -> None:
        await self.checkpoint()

    async def complete(self) -> None:
        await self.checkpoint()

    async def cancel(self) -> None:
        await self.checkpoint()

    async def shutdown(self) -> None:
        await self.checkpoint()


class DownloadEngine:
    def __init__(self) -> None:
        self.queue: list[str] = []
        self.active_tasks: dict[str, str] = {}
        self.sessions: dict[str, DownloadSession] = {}
        self.config = load()

    async def _db_updater(self, task_id: str, downloaded: int, total: int) -> None:
        # TODO: Implement actual SQLite update here
        pass

    async def download(
        self, url: str, dest: Path, progress_cb: Callable[..., Any] | None = None, task_id: str = ""
    ) -> None:
        session = DownloadSession(task_id, self._db_updater)
        if task_id:
            self.sessions[task_id] = session

        try:
            async with httpx.AsyncClient() as client, client.stream("GET", url) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                downloaded = 0
                with open(dest, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
                        downloaded += len(chunk)
                        await session.update_progress(downloaded, total)
                        if progress_cb:
                            if asyncio.iscoroutinefunction(progress_cb):
                                await progress_cb(downloaded, total)
                            else:
                                progress_cb(downloaded, total)
            await session.complete()
        except asyncio.CancelledError:
            await session.cancel()
            raise
        finally:
            if task_id:
                self.sessions.pop(task_id, None)

    async def pause(self, task_id: str) -> None:
        if session := self.sessions.get(task_id):
            await session.pause()
        
    async def resume(self, task_id: str) -> None:
        if session := self.sessions.get(task_id):
            await session.resume()
        
    async def cancel(self, task_id: str) -> None:
        if session := self.sessions.get(task_id):
            await session.cancel()
        
    async def retry(self, task_id: str) -> None:
        pass

    async def shutdown(self) -> None:
        for session in self.sessions.values():
            await session.shutdown()
        self.sessions.clear()


async def retry_task(task_id: str) -> None:
    pass

async def resume_task(task_id: str) -> None:
    pass

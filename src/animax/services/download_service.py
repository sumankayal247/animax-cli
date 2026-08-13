"""Download orchestration logic."""
from __future__ import annotations

import asyncio
from typing import Any
import logging
import shutil
import uuid
from pathlib import Path

import httpx

from animax.config.loader import load
from animax.models.download import ContentSource, DownloadStatus, DownloadTask

logger = logging.getLogger(__name__)

class DownloadEngine:
    def __init__(self) -> None:
        self.tasks: dict[str, DownloadTask] = {}
        self.active_processes: dict[str, asyncio.subprocess.Process] = {}
        self.active_tasks: dict[str, asyncio.Task[Any]] = {}
        self.config = load()

    async def _db_updater(self, task_id: str, downloaded: int, total: int) -> None:
        if task := self.tasks.get(task_id):
            task.bytes_downloaded = downloaded
            if total > 0:
                task.bytes_total = total
            if task.bytes_total:
                task.progress = (downloaded / task.bytes_total) * 100
        # TODO: Implement actual SQLite update here

    async def add_task(self, source: ContentSource, dest: str, media_id: str, episode: float) -> DownloadTask:
        task = DownloadTask(
            id=str(uuid.uuid4()),
            media_id=media_id,
            episode=episode,
            destination=dest,
            source=source,
            status=DownloadStatus.QUEUED,
        )
        self.tasks[task.id] = task
        # Automatically start it for now (Phase 5 queueing can be enhanced later)
        self.active_tasks[task.id] = asyncio.create_task(self._process_task(task))
        return task

    async def _process_task(self, task: DownloadTask) -> None:
        task.status = DownloadStatus.RUNNING
        try:
            if task.source.url.startswith("magnet:"):
                await self._download_magnet(task)
            else:
                await self._download_http(task)
            
            task.status = DownloadStatus.COMPLETED
            task.progress = 100.0
            
        except asyncio.CancelledError:
            task.status = DownloadStatus.CANCELLED
            logger.info(f"Task {task.id} cancelled.")
        except Exception as e:
            task.status = DownloadStatus.FAILED
            task.error = str(e)
            logger.error(f"Task {task.id} failed: {e}")
        finally:
            self.active_tasks.pop(task.id, None)

    async def _download_magnet(self, task: DownloadTask) -> None:
        if not shutil.which("aria2c"):
            raise RuntimeError("aria2c is required for magnet link downloads.")
            
        dest_path = Path(task.destination)
        dest_dir = dest_path.parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # We tell aria2c to download the magnet to the destination directory.
        # Aria2 will create a directory for the torrent contents.
        args = [
            "aria2c",
            "--seed-time=0",           # Don't seed after finishing
            "--bt-stop-timeout=300",   # Stop if metadata not found
            "--dir", str(dest_dir),
            task.source.url,
        ]
        
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        self.active_processes[task.id] = process
        
        # Read aria2c output to update progress (simplified)
        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                # Parse aria2c progress line here if needed
                
        await process.wait()
        self.active_processes.pop(task.id, None)
        
        if process.returncode != 0:
            raise RuntimeError(f"aria2c failed with code {process.returncode}")

    async def _download_http(self, task: DownloadTask) -> None:
        dest_path = Path(task.destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", task.source.url) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                task.bytes_total = total
                
                with open(dest_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
                        task.bytes_downloaded += len(chunk)
                        if total:
                            task.progress = (task.bytes_downloaded / total) * 100
                            
                        await self._db_updater(task.id, task.bytes_downloaded, total)

    async def cancel(self, task_id: str) -> None:
        if self.tasks.get(task_id):
            if process := self.active_processes.get(task_id):
                process.terminate()
            if asyncio_task := self.active_tasks.get(task_id):
                asyncio_task.cancel()

    async def shutdown(self) -> None:
        for task_id in list(self.active_tasks.keys()):
            await self.cancel(task_id)

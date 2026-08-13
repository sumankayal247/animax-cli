"""`anime download` — thin controller; logic lives in services (Phase 5)."""

from __future__ import annotations

import asyncio

import rich.console
import typer

from animax.models.plugin import PluginCategory
from animax.services.download_service import DownloadEngine
from animax.services.plugin_service import discover_plugins, get_plugin_manager


def register(app: typer.Typer) -> None:
    @app.command()
    def download(
        media_id: str = typer.Argument(..., help="Media id from a previous search (e.g. Anilist ID)."),
        episode: float = typer.Option(1.0, help="Episode number to download."),
    ) -> None:
        """Download an episode using available sources."""
        console = rich.console.Console()
        
        async def _run() -> None:
            from animax.services.plugin_service import get_provider_registry
            registry = get_provider_registry()
            await discover_plugins()
            
            # Find a metadata plugin to get details
            try:
                from animax.services.metadata_service import get_details
                item = await get_details(media_id)
            except Exception as e:
                console.print(f"[red]Failed to fetch metadata for {media_id}: {e}[/red]")
                return
                
            console.print(f"[cyan]Found media:[/cyan] {item.title}")
            
            # Find a source plugin
            source_records = [r for r in registry.enabled() if r.info.category.value == "source"]
            if not source_records:
                console.print("[red]No source plugins enabled![/red]")
                return
                
            sources = []
            with console.status("Resolving download sources..."):
                for record in source_records:
                    source_plugin = record.instance
                    try:
                        res = await source_plugin.resolve_source(item, episode)
                        sources.extend(res)
                    except Exception:
                        pass
            
            engine = DownloadEngine()
            dest = f"./downloads/{item.title}"
            if item.media_type.value != "Movie":
                dest += f" - {episode:02g}"
                
            task_success = False
            
            for idx, source in enumerate(sources):
                console.print(f"\n[cyan]Attempting Source {idx+1}/{len(sources)} from {source.plugin}...[/cyan]")
                task = await engine.add_task(source, dest, media_id, episode)
                
                # Wait for completion using a progress bar
                from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
                with Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:
                    pid = progress.add_task("[cyan]Downloading...", total=100.0)
                    
                    while task.status in ("queued", "running"):
                        progress.update(pid, completed=task.progress)
                        await asyncio.sleep(0.5)
                        
                    progress.update(pid, completed=task.progress)
                    
                if task.status == "completed":
                    console.print("[bold green]Download Complete![/bold green]")
                    from animax.services.history_service import log_event
                    from animax.services.library_service import update_progress
                    await log_event(media_id, item.title, episode, "Download", source.plugin)
                    await update_progress(media_id, item.title, episode, 0.0, source.plugin)
                    task_success = True
                    break
                else:
                    console.print(f"[yellow]Download failed:[/] {task.error}")
                    console.print("[dim]Trying next source if available...[/dim]")
                    
            if not task_success:
                console.print("\n[bold red]All available sources failed to download![/bold red]")
                
        asyncio.run(_run())

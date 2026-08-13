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
            metadata_records = [r for r in registry.enabled() if r.info.category.value == "metadata"]
            if not metadata_records:
                console.print("[red]No metadata plugins enabled![/red]")
                return
            
            meta_plugin = metadata_records[0].instance
            try:
                item = await meta_plugin.get_details(media_id)
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
            for record in source_records:
                source_plugin = record.instance
                try:
                    res = await source_plugin.resolve_source(item, episode)
                    sources.extend(res)
                except Exception:
                    pass
            
            if not sources:
                console.print(f"[red]No downloadable sources found for Episode {episode}[/red]")
                return
                
            best_source = sources[0]
            console.print(f"[green]Found source from {best_source.plugin}:[/green] {best_source.url[:60]}...")
            
            # Queue download
            engine = DownloadEngine()
            dest = f"./downloads/{item.title} - {episode:02g}"
            
            task = await engine.add_task(best_source, dest, media_id, episode)
            console.print(f"[yellow]Downloading to {dest}...[/yellow]")
            
            # Wait for completion
            while task.status in ("queued", "running"):
                await asyncio.sleep(0.5)
                
            if task.status == "completed":
                console.print("[bold green]Download Complete![/bold green]")
                from animax.services.history_service import log_event
                from animax.services.library_service import update_progress
                await log_event(media_id, item.title, episode, "Download", best_source.plugin)
                await update_progress(media_id, item.title, episode, 0.0, best_source.plugin)
            else:
                console.print(f"[bold red]Download failed: {task.error}[/bold red]")
                
        asyncio.run(_run())

"""`anime download` — thin controller; logic lives in services (Phase 5)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


import asyncio
import rich.console
from animax.services.plugin_service import get_plugin_manager, discover_plugins
from animax.services.download_service import DownloadEngine
from animax.models.plugin import PluginCategory
from animax.core.interfaces.metadata import MetadataPlugin
from animax.core.interfaces.source import SourcePlugin

def register(app: typer.Typer) -> None:
    @app.command()
    def download(
        media_id: str = typer.Argument(..., help="Media id from a previous search (e.g. Anilist ID)."),
        episode: float = typer.Option(1.0, help="Episode number to download."),
    ) -> None:
        """Download an episode using available sources."""
        console = rich.console.Console()
        
        async def _run() -> None:
            pm = get_plugin_manager()
            await discover_plugins()
            
            # Find a metadata plugin to get details
            metadata_records = pm.enabled(PluginCategory.METADATA)
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
            source_records = pm.enabled(PluginCategory.SOURCE)
            if not source_records:
                console.print("[red]No source plugins enabled![/red]")
                return
                
            sources = []
            for record in source_records:
                source_plugin = record.instance
                try:
                    res = await source_plugin.resolve_source(item, episode)
                    sources.extend(res)
                except Exception as e:
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
            while task.status == "running":
                await asyncio.sleep(1.0)
                
            if task.status == "completed":
                console.print("[bold green]Download Complete![/bold green]")
            else:
                console.print(f"[bold red]Download failed: {task.error}[/bold red]")
                
        asyncio.run(_run())

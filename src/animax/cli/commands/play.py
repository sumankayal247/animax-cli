"""`anime play` — thin controller; logic lives in services (Phase 5)."""

from __future__ import annotations

import asyncio

import rich.console
import typer

from animax.services.player_service import play_media


def register(app: typer.Typer) -> None:
    @app.command()
    def play(
        media_id: str = typer.Argument(..., help="Media id, or a local file path."),
        episode: str | None = typer.Option(None, help="Episode number to play."),
        player: str | None = typer.Option(None, "--player", "-p", help="Preferred player plugin (e.g. mpv, vlc)."),
    ) -> None:
        """Play a downloaded or streamed episode in the configured player."""
        console = rich.console.Console()
        
        async def _run() -> None:
            from animax.services.plugin_service import get_provider_registry, discover_plugins
            registry = get_provider_registry()
            await discover_plugins()
            
            # If media_id is a file or url, play it directly
            import os
            if os.path.exists(media_id) or media_id.startswith("http"):
                try:
                    await play_media(media_id, preferred_player=player)
                except Exception as e:
                    console.print(f"[red]Error playing media: {e}[/red]")
                return

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
            
            source_records = [r for r in registry.enabled() if r.info.category.value == "source"]
            if not source_records:
                console.print("[red]No source plugins enabled![/red]")
                return
                
            sources = []
            with console.status("Resolving streaming sources..."):
                for record in source_records:
                    source_plugin = record.instance
                    try:
                        # If episode is None, it defaults to 1.0 just to get a source
                        ep_num = float(episode) if episode else 1.0
                        res = await source_plugin.resolve_source(item, ep_num)
                        sources.extend(res)
                    except Exception:
                        pass
            
            if not sources:
                console.print(f"[red]No playable sources found.[/red]")
                return
                
            best_source = sources[0]
            
            if best_source.url.startswith("magnet:"):
                console.print(f"\n[yellow]Warning:[/yellow] The best source found is a Torrent (Magnet link).")
                console.print(f"[red]MPV and VLC cannot stream raw magnet links directly yet![/red]")
                console.print(f"\n[green]Please download it first using:[/green]")
                console.print(f"  [bold]anime download '{media_id}'" + (f" --episode {episode}" if episode else "") + "[/bold]\n")
                return

            console.print(f"[green]Playing source from {best_source.plugin}...[/green]")
            try:
                await play_media(best_source.url, preferred_player=player)
            except Exception as e:
                console.print(f"[red]Error playing media: {e}[/red]")
                
        asyncio.run(_run())

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

            try:
                from animax.services.metadata_service import get_details
                item = await get_details(media_id)
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
                import shutil
                if not shutil.which("npx"):
                    console.print(f"\n[yellow]Warning:[/yellow] The best source found is a Torrent (Magnet link).")
                    console.print(f"[red]To stream magnets instantly, you need 'NodeJS' (npx) installed![/red]")
                    console.print(f"Or download it first using: [bold]anime download '{media_id}'" + (f" --episode {episode}" if episode else "") + "[/bold]\n")
                    return
                else:
                    console.print(f"[green]Streaming Magnet link via Peerflix...[/green]")
                    console.print(f"[yellow]Connecting to trackers and peers... (This may take a moment. If it hangs, your ISP might be blocking torrents.)[/yellow]")
                    import subprocess
                    import sys
                    import random
                    
                    random_port = str(random.randint(50000, 60000))
                    cmd = ["npx", "-y", "peerflix", best_source.url, "--peer-port", random_port, "--connections", "200"]
                    if player == "vlc":
                        cmd.append("--vlc")
                    else:
                        cmd.append("--mpv")
                        
                    try:
                        subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
                    except Exception as e:
                        console.print(f"[red]Error streaming media: {e}[/red]")
                    return

            console.print(f"[green]Playing source from {best_source.plugin}...[/green]")
            try:
                from animax.services.player_service import play_media
                await play_media(best_source.url, preferred_player=player)
            except Exception as e:
                console.print(f"[red]Error playing media: {e}[/red]")
                
        asyncio.run(_run())

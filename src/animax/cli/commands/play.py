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
        
        # For Phase 5, just support local files/URLs directly via media_id
        # Later we can look up the library/downloads if media_id is a UUID
        target = media_id
        
        try:
            asyncio.run(play_media(target, preferred_player=player))
        except Exception as e:
            console.print(f"[red]Error playing media: {e}[/red]")
            raise typer.Exit(1)

"""`anime play` — thin controller; logic lives in services (Phase 5)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def play(
        media_id: str = typer.Argument(..., help="Media id, or a local file path."),
        episode: str | None = typer.Option(None, help="Episode number to play."),
    ) -> None:
        """Play a downloaded or streamed episode in the configured player."""
        not_yet_implemented("anime play", "Phase 5 (download framework & player integration)")

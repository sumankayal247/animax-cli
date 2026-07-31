"""`anime download` — thin controller; logic lives in services (Phase 5)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def download(
        media_id: str = typer.Argument(..., help="Media id from a previous search."),
        episode: str | None = typer.Option(None, help="Episode number, or range, to download."),
    ) -> None:
        """Download one or more episodes."""
        not_yet_implemented("anime download", "Phase 5 (download framework & player integration)")

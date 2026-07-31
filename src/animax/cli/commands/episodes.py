"""`anime episodes` — thin controller; logic lives in services (Phase 4)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def episodes(
        media_id: str = typer.Argument(..., help="Media id from a previous search."),
    ) -> None:
        """List episodes for a media item."""
        not_yet_implemented("anime episodes", "Phase 4 (metadata plugin framework)")

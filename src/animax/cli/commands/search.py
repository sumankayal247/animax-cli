"""`anime search` — thin controller; logic lives in services (Phase 4)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def search(query: str = typer.Argument(..., help="Title to search for.")) -> None:
        """Search enabled metadata and search plugins for a title."""
        not_yet_implemented("anime search", "Phase 4 (metadata plugin framework)")

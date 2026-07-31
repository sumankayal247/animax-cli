"""`anime library` — thin controller; logic lives in services (Phase 6)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def library() -> None:
        """Browse your local library: favorites, downloads, resume state."""
        not_yet_implemented("anime library", "Phase 6 (library & history)")

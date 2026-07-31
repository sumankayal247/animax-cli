"""`anime history` — thin controller; logic lives in services (Phase 6)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def history() -> None:
        """Show your watch/download history."""
        not_yet_implemented("anime history", "Phase 6 (library & history)")

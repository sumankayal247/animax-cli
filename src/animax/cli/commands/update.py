"""`anime update` — thin controller; logic lives in services (Phase 7)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def update() -> None:
        """Check for and install Animax-Cli updates."""
        not_yet_implemented("anime update", "Phase 7 (installer & release tooling)")

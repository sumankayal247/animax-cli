"""`anime logs` — thin controller; logic lives in services (Phase 6)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def logs() -> None:
        """View recent log output."""
        not_yet_implemented("anime logs", "Phase 6 (configuration & logging polish)")

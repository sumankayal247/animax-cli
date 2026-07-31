"""`anime diagnose` — deeper diagnostics than `doctor`; logic lives in services (Phase 7)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def diagnose() -> None:
        """Run an extended diagnostic report (plugin health, connectivity, disk space)."""
        not_yet_implemented("anime diagnose", "Phase 7 (installer & doctor)")

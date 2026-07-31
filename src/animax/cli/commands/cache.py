"""`anime cache` — thin controller; logic lives in services (Phase 6)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def cache() -> None:
        """Inspect or clear the on-disk cache."""
        not_yet_implemented("anime cache", "Phase 6 (cache management)")

"""`anime about`."""

from __future__ import annotations

import typer

from animax import __version__
from animax.core.constants import APP_NAME
from animax.ui.theme import console


def register(app: typer.Typer) -> None:
    @app.command()
    def about() -> None:
        """Show information about Animax-Cli."""
        console.print(
            f"[animax.title]{APP_NAME}[/] v{__version__}\n"
            "A modern, plugin-based terminal media CLI framework.\n"
            "Licensed under the Apache License 2.0."
        )

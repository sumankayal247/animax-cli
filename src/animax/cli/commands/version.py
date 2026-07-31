"""`anime version`."""

from __future__ import annotations

import typer

from animax import __version__
from animax.core.constants import APP_NAME
from animax.ui.theme import console


def register(app: typer.Typer) -> None:
    @app.command()
    def version() -> None:
        """Print the Animax-Cli version."""
        console.print(f"{APP_NAME} {__version__}")

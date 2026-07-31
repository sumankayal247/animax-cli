"""The Typer-based CLI. Command modules under cli.commands are thin controllers
that call into services for all business logic.
"""

from animax.cli.app import app

__all__ = ["app"]

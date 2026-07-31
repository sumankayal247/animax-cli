"""`anime config` — thin controller over services.config_service."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented
from animax.config import paths as config_paths
from animax.services.config_service import load_settings
from animax.ui.theme import console

config_app = typer.Typer(help="Inspect and manage Animax-Cli configuration.")


@config_app.command("show")
def show() -> None:
    """Print the currently resolved configuration."""
    settings = load_settings()
    console.print_json(settings.model_dump_json())


@config_app.command("path")
def path() -> None:
    """Print the path to the configuration file."""
    console.print(str(config_paths.config_file()))


@config_app.command("set")
def set_value(
    key: str = typer.Argument(..., help="Dotted config key, e.g. download.retries"),
    value: str = typer.Argument(..., help="New value."),
) -> None:
    """Set a configuration value."""
    not_yet_implemented("anime config set", "Phase 6 (configuration polish)")


def register(app: typer.Typer) -> None:
    app.add_typer(config_app, name="config")

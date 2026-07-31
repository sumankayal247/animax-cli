"""Builds the root Typer application and wires up every command module."""

from __future__ import annotations

import typer

from animax.cli.commands import (
    about,
    cache,
    config,
    diagnose,
    doctor,
    download,
    episodes,
    history,
    info,
    library,
    logs,
    play,
    plugins,
    search,
    update,
    version,
)
from animax.core.constants import APP_NAME, COMMAND_NAME
from animax.logging_config import configure_logging

app = typer.Typer(
    name=COMMAND_NAME,
    help=f"{APP_NAME} — a modern, plugin-based terminal media CLI framework.",
    no_args_is_help=True,
)


@app.callback()
def main_callback(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging and tracebacks."),
) -> None:
    configure_logging(debug=debug)


_COMMAND_MODULES = (
    search,
    info,
    episodes,
    download,
    play,
    library,
    history,
    config,
    plugins,
    doctor,
    logs,
    cache,
    update,
    version,
    about,
    diagnose,
)

for _module in _COMMAND_MODULES:
    _module.register(app)

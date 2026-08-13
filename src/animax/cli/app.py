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
    import asyncio

    from animax.database.connection import initialize
    configure_logging(debug=debug)
    
    try:
        from animax.config.paths import database_file
        db_path = database_file()
        is_first_run = not db_path.exists()
        
        asyncio.run(initialize())
        
        if is_first_run:
            from rich.console import Console
            Console().print("\n[bold green]Welcome to Animax CLI![/bold green] 🎉")
            Console().print("💡 [cyan]Tip: You can install this CLI globally so you don't need 'uv run'![/cyan]")
            Console().print("Just run: [bold]uv tool install .[/bold]\n")
            
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to initialize database: {e}")


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

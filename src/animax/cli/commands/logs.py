"""`anime logs` — thin controller; logic lives in services (Phase 6)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


import rich.console
from animax.config.paths import log_dir

def register(app: typer.Typer) -> None:
    @app.command()
    def logs(
        lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
    ) -> None:
        """View recent log output."""
        console = rich.console.Console()
        
        log_file = log_dir() / "animax.log"
        if not log_file.exists():
            console.print("No log file found.")
            return
            
        with open(log_file, "r") as f:
            all_lines = f.readlines()
            
        tail = all_lines[-lines:]
        for line in tail:
            console.print(line, end="")

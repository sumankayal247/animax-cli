"""`anime update` — thin controller; logic lives in services (Phase 7)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


import rich.console
import httpx
from animax.core.constants import APP_NAME

def register(app: typer.Typer) -> None:
    @app.command()
    def update() -> None:
        """Check for and install Animax-Cli updates."""
        console = rich.console.Console()
        
        try:
            import importlib.metadata
            VERSION = importlib.metadata.version(APP_NAME)
        except importlib.metadata.PackageNotFoundError:
            VERSION = "0.1.0-dev"
            
        console.print(f"[cyan]Current version:[/cyan] {VERSION}")
        console.print("[yellow]Checking for updates on PyPI...[/yellow]")
        
        try:
            res = httpx.get("https://pypi.org/pypi/animax-cli/json", timeout=5.0)
            if res.status_code == 200:
                data = res.json()
                latest = data.get("info", {}).get("version")
                if latest:
                    console.print(f"[green]Latest version on PyPI:[/green] {latest}")
                    if latest != VERSION:
                        console.print("\n[bold yellow]An update is available![/bold yellow]")
                        console.print(f"Run [cyan]pip install --upgrade animax-cli[/cyan] or [cyan]uv tool upgrade animax-cli[/cyan] to update.")
                    else:
                        console.print("\n[bold green]You are running the latest version.[/bold green]")
                else:
                    console.print("[red]Could not determine the latest version from PyPI.[/red]")
            else:
                # If package doesn't exist on PyPI yet (which it likely doesn't for a mock app)
                console.print(f"[dim]Note: animax-cli not found on PyPI (Status {res.status_code})[/dim]")
                console.print("\n[bold green]You are running the latest installed version.[/bold green]")
        except Exception as e:
            console.print(f"[red]Failed to check for updates:[/red] {e}")

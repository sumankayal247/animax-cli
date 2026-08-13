"""`anime diagnose` — deeper diagnostics than `doctor`; logic lives in services (Phase 7)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


import asyncio
import os
import shutil
import platform
import rich.console
from rich.table import Table
from animax.config.paths import data_dir

def register(app: typer.Typer) -> None:
    @app.command()
    def diagnose() -> None:
        """Run an extended diagnostic report (plugin health, connectivity, disk space)."""
        console = rich.console.Console()
        console.print("[bold cyan]System Diagnostics Report[/bold cyan]\n")
        
        table = Table(title="System Information")
        table.add_column("Component", style="magenta")
        table.add_column("Status / Info", style="green")
        
        # 1. OS & Platform
        table.add_row("OS", f"{platform.system()} {platform.release()}")
        table.add_row("Python", platform.python_version())
        
        # 2. Disk Space
        d_dir = data_dir()
        if not d_dir.exists():
            d_dir.mkdir(parents=True, exist_ok=True)
            
        total, used, free = shutil.disk_usage(d_dir)
        free_gb = free / (1024 ** 3)
        table.add_row("Data Directory", str(d_dir))
        table.add_row("Free Space", f"{free_gb:.2f} GB")
        
        # 3. External Binaries
        aria2c = shutil.which("aria2c")
        table.add_row("aria2c (Downloads)", "Found" if aria2c else "[yellow]Missing[/yellow]")
        
        mpv = shutil.which("mpv")
        table.add_row("mpv (Player)", "Found" if mpv else "[yellow]Missing[/yellow]")
        
        vlc = shutil.which("vlc") or shutil.which("cvlc")
        table.add_row("vlc (Player)", "Found" if vlc else "[yellow]Missing[/yellow]")
        
        console.print(table)
        
        # 4. Network Connectivity
        console.print("\n[bold cyan]Checking Network Connectivity...[/bold cyan]")
        import httpx
        try:
            res = httpx.get("https://1.1.1.1", timeout=5.0)
            if res.status_code == 200 or res.status_code == 301:
                console.print("[green]✔ Internet Connection: OK[/green]")
            else:
                console.print(f"[yellow]⚠ Internet Connection: Unexpected status {res.status_code}[/yellow]")
        except Exception as e:
            console.print(f"[red]✖ Internet Connection: Failed ({e})[/red]")
        
        console.print("\n[bold]Diagnostics complete.[/bold]")

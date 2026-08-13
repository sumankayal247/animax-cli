"""`anime history` — thin controller; logic lives in services (Phase 6)."""

from __future__ import annotations

import asyncio
import datetime

import rich.console
import typer
from rich.table import Table

from animax.services.history_service import clear_history, get_history


def register(app: typer.Typer) -> None:
    @app.command()
    def history(
        clear: bool = typer.Option(False, "--clear", help="Clear all history"),
        limit: int = typer.Option(50, "--limit", "-n", help="Number of entries to show"),
    ) -> None:
        """Show your watch/download history."""
        console = rich.console.Console()
        
        async def _run() -> None:
            if clear:
                await clear_history()
                console.print("[green]History cleared successfully.[/green]")
                return
                
            entries = await get_history(limit=limit)
            if not entries:
                console.print("History is empty.")
                return
                
            table = Table(title="Watch & Download History")
            table.add_column("Date", style="dim")
            table.add_column("Title", style="cyan")
            table.add_column("Episode", justify="right", style="magenta")
            table.add_column("Event", justify="center")
            table.add_column("Plugin", style="green")
            
            for row in entries:
                date_str = datetime.datetime.fromtimestamp(row["occurred_at"]).strftime("%Y-%m-%d %H:%M")
                table.add_row(
                    date_str,
                    row["title"],
                    str(row["episode"]),
                    row["event"],
                    row.get("plugin_used", "N/A")
                )
                
            console.print(table)
            
        asyncio.run(_run())

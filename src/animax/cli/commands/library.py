"""`anime library` — thin controller; logic lives in services (Phase 6)."""

from __future__ import annotations

import asyncio

import rich.console
import typer
from rich.table import Table

from animax.services.library_service import get_library


def register(app: typer.Typer) -> None:
    @app.command()
    def library() -> None:
        """Browse your local library: favorites, downloads, resume state."""
        console = rich.console.Console()
        
        async def _run() -> None:
            entries = await get_library()
            if not entries:
                console.print("Library is empty.")
                return
                
            table = Table(title="Local Library")
            table.add_column("Title", style="cyan")
            table.add_column("Last Episode", justify="right", style="magenta")
            table.add_column("Favorite", justify="center")
            table.add_column("Plugin", style="green")
            
            for row in entries:
                fav = "⭐" if row["is_favorite"] else ""
                table.add_row(
                    row["title"],
                    str(row.get("last_episode", "N/A")),
                    fav,
                    row.get("plugin_used", "N/A")
                )
                
            console.print(table)
            
        asyncio.run(_run())

"""`anime search` — thin controller; logic lives in services (Phase 4)."""

from __future__ import annotations

import typer

from animax.cli.commands._common import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command()
    def search(query: str = typer.Argument(..., help="Title to search for.")) -> None:
        """Search enabled metadata and search plugins for a title."""
        import asyncio
        from rich.console import Console
        from animax.services.search_service import search as search_srv
        from animax.ui.tables import metadata_table
        
        console = Console()
        with console.status(f"Searching for '{query}'..."):
            try:
                results = asyncio.run(search_srv(query))
            except Exception as e:
                console.print(f"[red]Error searching:[/] {e}")
                return
                
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return
            
        items = [r.item for r in results]
        table = metadata_table(items)
        console.print(table)

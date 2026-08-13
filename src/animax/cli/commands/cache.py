"""`anime cache` — thin controller; logic lives in services (Phase 6)."""

from __future__ import annotations

import rich.console
import typer

from animax.cache.store import Cache
from animax.config.paths import cache_dir


def register(app: typer.Typer) -> None:
    @app.command()
    def cache(
        clear: bool = typer.Option(False, "--clear", help="Clear all caches"),
        namespace: str = typer.Option(None, "--namespace", "-n", help="Specific cache namespace"),
    ) -> None:
        """Inspect or clear the on-disk cache."""
        console = rich.console.Console()
        
        base_dir = cache_dir()
        if not base_dir.exists():
            console.print("No cache directory found.")
            return
            
        if clear:
            if namespace:
                Cache(namespace).clear()
                console.print(f"[green]Cleared cache namespace '{namespace}'.[/green]")
            else:
                import shutil
                shutil.rmtree(base_dir)
                base_dir.mkdir()
                console.print("[green]Cleared all caches.[/green]")
            return
            
        # Inspect mode
        console.print("[bold]Cache Size:[/bold]")
        total_size = 0
        
        for ns_dir in base_dir.iterdir():
            if ns_dir.is_dir():
                ns_size = sum(f.stat().st_size for f in ns_dir.glob("*.json"))
                total_size += ns_size
                console.print(f"  {ns_dir.name}: {ns_size / 1024:.2f} KB")
                
        console.print(f"\n[bold]Total:[/bold] {total_size / 1024 / 1024:.2f} MB")

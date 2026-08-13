"""`anime search` — thin controller; logic lives in services (Phase 4)."""

from __future__ import annotations

import typer

def register(app: typer.Typer) -> None:
    @app.command()
    def search(query: str = typer.Argument(..., help="Title to search for.")) -> None:
        """Search enabled metadata and search plugins for a title."""
        import asyncio
        from rich.console import Console
        import questionary
        from animax.services.search_service import search as search_srv
        from animax.services.metadata_service import get_details, get_episodes
        from animax.ui.tables import metadata_table
        
        console = Console()
        
        # Support using '_' instead of spaces in CLI
        query = query.replace("_", " ")
        
        with console.status(f"Searching for '{query}'..."):
            try:
                results = asyncio.run(search_srv(query))
            except Exception as e:
                console.print(f"[red]Error searching:[/] {e}")
                return
                
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return
            
        while True:
            choices = []
            for r in results:
                title = r.item.title
                year = r.item.year or "—"
                eps = r.item.episode_count or "—"
                choices.append(questionary.Choice(title=f"{title} ({year}) - {eps} eps", value=r.item))
            
            choices.append(questionary.Choice(title="[Exit]", value=None))
            
            selected_item = questionary.select(
                "Select a media item to explore:",
                choices=choices
            ).ask()
            
            if not selected_item:
                break
                
            while True:
                action = questionary.select(
                    f"What would you like to do with '{selected_item.title}'?",
                    choices=[
                        questionary.Choice(title="Show Info", value="info"),
                        questionary.Choice(title="List Episodes", value="episodes"),
                        questionary.Choice(title="Go Back to Search Results", value="back"),
                        questionary.Choice(title="Exit", value="exit"),
                    ]
                ).ask()
                
                if action == "exit" or action is None:
                    return
                elif action == "back":
                    break
                elif action == "info":
                    with console.status("Fetching details..."):
                        try:
                            # Prefer the first source plugin of the item
                            details = asyncio.run(get_details(selected_item.id, provider=selected_item.source_plugins[0] if selected_item.source_plugins else None))
                            console.print(f"\n[bold cyan]{details.title}[/bold cyan]")
                            console.print(f"[yellow]Synopsis:[/] {details.synopsis or 'No synopsis available.'}")
                            console.print(f"[yellow]Year:[/] {details.year}")
                            console.print(f"[yellow]Episodes:[/] {details.episode_count}\n")
                        except Exception as e:
                            console.print(f"[red]Failed to fetch details:[/] {e}")
                elif action == "episodes":
                    with console.status("Fetching episodes..."):
                        try:
                            eps = asyncio.run(get_episodes(selected_item.id, provider=selected_item.source_plugins[0] if selected_item.source_plugins else None))
                            if not eps:
                                console.print("[yellow]No episodes found.[/yellow]")
                            else:
                                console.print(f"\n[bold cyan]Episodes for {selected_item.title}:[/bold cyan]")
                                for ep in eps:
                                    console.print(f"  [green]Episode {ep.number}[/green]: {ep.title or 'No title'}")
                                console.print()
                        except Exception as e:
                            console.print(f"[red]Failed to fetch episodes:[/] {e}")

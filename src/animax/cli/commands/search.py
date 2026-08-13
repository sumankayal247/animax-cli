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
            
        from textual.app import App, ComposeResult
        from textual.widgets import DataTable, Footer, Header
        from textual.binding import Binding

        class SearchSelectionApp(App):
            CSS = "DataTable { height: 100%; }"
            BINDINGS = [
                Binding("escape", "quit", "Quit", show=True),
            ]

            def __init__(self, results):
                super().__init__()
                self.results_data = results
                self.selected_item = None

            def compose(self) -> ComposeResult:
                yield Header(show_clock=False)
                yield DataTable(cursor_type="row")
                yield Footer()

            def on_mount(self) -> None:
                table = self.query_one(DataTable)
                table.add_columns("Title", "Year", "Episodes", "Sources")
                for idx, r in enumerate(self.results_data):
                    table.add_row(
                        r.item.title,
                        str(r.item.year) if r.item.year else "—",
                        str(r.item.episode_count) if r.item.episode_count else "—",
                        ", ".join(r.item.source_plugins) or "—",
                        key=str(idx)
                    )
                table.focus()

            def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
                idx = int(event.row_key.value)
                self.selected_item = self.results_data[idx].item
                self.exit(self.selected_item)

        while True:
            app_ui = SearchSelectionApp(results)
            selected_item = app_ui.run()
            
            if not selected_item:
                break
                
            while True:
                import questionary
                action = questionary.select(
                    f"What would you like to do with '{selected_item.title}'?",
                    choices=[
                        questionary.Choice(title="Show Info", value="info"),
                        questionary.Choice(title="List Episodes", value="episodes"),
                        questionary.Choice(title="Download Episode", value="download"),
                        questionary.Choice(title="Play Episode", value="play"),
                        questionary.Choice(title="Go Back to Search Results", value="back"),
                        questionary.Choice(title="Exit", value="exit"),
                    ]
                ).ask()
                
                if action == "exit" or action is None:
                    return
                elif action == "back":
                    break
                elif action == "download":
                    from animax.models.media import MediaType
                    if selected_item.media_type == MediaType.MOVIE:
                        console.print(f"\n[green]To download this movie, run:[/] [bold]anime download '{selected_item.id}'[/bold]")
                    else:
                        ep_num = questionary.text("Enter episode number to download (e.g. 1):").ask()
                        if ep_num and ep_num.replace(".", "").isdigit():
                            console.print(f"\n[green]To download, run:[/] [bold]anime download '{selected_item.id}' --episode {ep_num}[/bold]")
                            console.print("[dim](Or implement direct downloading here in the future)[/dim]\n")
                elif action == "info":
                    with console.status("Fetching details..."):
                        try:
                            from animax.services.metadata_service import get_details
                            details = asyncio.run(get_details(selected_item.id))
                            
                            console.print(f"\n[bold cyan]{details.title}[/bold cyan]")
                            console.print(f"[yellow]Synopsis:[/] {details.synopsis or 'No synopsis available.'}")
                            console.print(f"[yellow]Year:[/] {details.year}")
                            if details.media_type.value != "Movie":
                                console.print(f"[yellow]Episodes:[/] {details.episode_count}\n")
                            else:
                                console.print("[yellow]Type:[/] Movie\n")
                        except Exception as e:
                            console.print(f"[red]Failed to fetch details:[/] {e}")
                elif action == "episodes":
                    with console.status("Fetching episodes..."):
                        try:
                            from animax.services.metadata_service import get_episodes
                            eps = asyncio.run(get_episodes(selected_item.id))
                            
                            if eps:
                                console.print(f"\n[bold cyan]Episodes for {selected_item.title}:[/bold cyan]")
                                for ep in eps:
                                    console.print(f"  {ep.number:02g}. {ep.title or 'Episode ' + str(ep.number)}")
                                console.print()
                            else:
                                console.print("\n[yellow]No episodes found.[/yellow]\n")
                        except Exception as e:
                            console.print(f"[red]Failed to fetch episodes:[/] {e}")
                elif action == "play":
                    ep_num = questionary.text("Enter episode number to play (e.g. 1):").ask()
                    if ep_num and ep_num.replace(".", "").isdigit():
                        console.print(f"\n[green]To play, run:[/] [bold]anime play '{selected_item.id}' --episode {ep_num}[/bold]")
                        console.print("[dim](Or implement direct playing here in the future)[/dim]\n")

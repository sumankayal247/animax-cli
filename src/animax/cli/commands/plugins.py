"""`anime plugins` — thin controller over services.plugin_service."""

from __future__ import annotations

import typer

from animax.services.plugin_service import discover_plugins
from animax.ui.plugins import render_plugin_table
from animax.ui.theme import console


def register(app: typer.Typer) -> None:
    @app.command()
    def plugins() -> None:
        """List discovered plugins, their source, priority, and health."""
        import asyncio
        records, warnings = asyncio.run(discover_plugins())
        render_plugin_table(records)
        for warning in warnings:
            console.print(f"[animax.warning]Warning:[/] {warning}")

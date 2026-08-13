"""`anime plugins` — thin controller over services.plugin_service."""

from __future__ import annotations

import typer

from animax.services.plugin_service import discover_plugins, get_provider_registry
from animax.ui.plugins import render_plugin_table
from animax.ui.theme import console


def register(app: typer.Typer) -> None:
    @app.command()
    def plugins() -> None:
        """List discovered plugins, their source, priority, and health."""
        import asyncio
        _, warnings = asyncio.run(discover_plugins())
        records = get_provider_registry().enabled()
        render_plugin_table(records)
        for warning in warnings:
            console.print(f"[animax.warning]Warning:[/] {warning}")

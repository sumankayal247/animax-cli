"""Renders the plugin registry as a Rich table for `anime plugins`."""

from __future__ import annotations

from rich.table import Table

from animax.models.provider import ProviderRecord
from animax.ui.theme import console


def render_plugin_table(records: list[ProviderRecord]) -> None:
    table = Table(title="Plugins")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Plugin")
    table.add_column("Priority", justify="right")
    table.add_column("Enabled")
    table.add_column("Health")

    for record in records:
        enabled = "[animax.success]yes[/]" if record.enabled else "[animax.muted]no[/]"
        table.add_row(
            record.info.name,
            record.info.category.value,
            record.plugin_name,
            str(record.info.priority),
            enabled,
            record.health.value,
        )

    console.print(table)
    if not records:
        console.print(
            "[animax.muted]No plugins discovered yet — bundled metadata/download/streaming "
            "plugins land in Phase 4/5. Drop your own into the user plugin directory any time "
            "(see `anime config path`).[/]"
        )

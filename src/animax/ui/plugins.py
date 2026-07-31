"""Renders the plugin registry as a Rich table for `anime plugins`."""

from __future__ import annotations

from rich.table import Table

from animax.models.plugin import PluginRecord
from animax.ui.theme import console


def render_plugin_table(records: list[PluginRecord]) -> None:
    table = Table(title="Plugins")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Version")
    table.add_column("Source")
    table.add_column("Priority", justify="right")
    table.add_column("Enabled")
    table.add_column("Health")

    for record in records:
        enabled = "[animax.success]yes[/]" if record.enabled else "[animax.muted]no[/]"
        if record.shadowed_by:
            enabled += f" [animax.muted](shadowed by {record.shadowed_by})[/]"
        table.add_row(
            record.info.name,
            record.info.category.value,
            record.info.version,
            record.source.value,
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

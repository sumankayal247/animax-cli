"""Reusable Rich tables. Commands never construct `rich.table.Table` directly
— they call one of these, or `build_table()` for something ad hoc.

Every table built here gets: ASCII-safe box drawing when ui.runtime is in
ascii_mode, column wrapping for long text (`overflow="fold"`), and Rich's
own automatic terminal-resize handling (Table recomputes column widths on
every render against the live console width — nothing extra needed here
for that part).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal

from rich import box
from rich.table import Table

from animax.models.download import DownloadTask
from animax.models.library import HistoryEntry, LibraryEntry
from animax.models.media import MediaItem
from animax.models.provider import ProviderRecord
from animax.ui.renderers import styles
from animax.ui.runtime import get_state
from animax.ui.status import StatusKind, status_markup

Justify = Literal["left", "center", "right"]


def _box_style() -> box.Box:
    return box.ASCII if get_state().ascii_mode else box.ROUNDED


def build_table(
    title: str,
    columns: Sequence[str],
    rows: Iterable[Sequence[Any]],
    *,
    justify: Sequence[Justify] | None = None,
    sort_key: Callable[[Sequence[Any]], Any] | None = None,
    sort_reverse: bool = False,
) -> Table:
    """A generic table: pass column headers and row tuples.

    ``sort_key``/``sort_reverse`` sort the rows before rendering — the one
    piece of "business logic" this module allows itself, since it's purely
    about presentation order, not data selection.
    """
    row_list = list(rows)
    if sort_key is not None:
        row_list.sort(key=sort_key, reverse=sort_reverse)

    table = Table(title=title, box=_box_style(), show_lines=False)
    for i, column in enumerate(columns):
        column_justify: Justify = justify[i] if justify else "left"
        table.add_column(column, justify=column_justify, overflow="fold")
    for row in row_list:
        table.add_row(*(str(cell) for cell in row))
    return table


def plugins_table(records: Sequence[ProviderRecord]) -> Table:
    """Every field a provider declares."""
    table = Table(title="Plugins", box=_box_style())
    plugin_columns: tuple[tuple[str, Justify], ...] = (
        ("Name", "left"),
        ("Category", "left"),
        ("Plugin", "left"),
        ("Priority", "right"),
        ("Capabilities", "left"),
        ("Status", "left"),
        ("Health", "left"),
    )
    for column, justify in plugin_columns:
        table.add_column(column, justify=justify, overflow="fold")

    for record in records:
        status = status_markup(
            "success" if record.enabled else "pending", "enabled" if record.enabled else "disabled"
        )
        health_kind: StatusKind = "success" if record.health.value == "healthy" else "warning"
        caps = [k for k, v in record.info.capabilities.model_dump().items() if v]
        capabilities = ", ".join(sorted(caps)) or f"[{styles.MUTED}]—[/]"
        table.add_row(
            record.info.name,
            record.info.category.value,
            record.plugin_name,
            str(record.info.priority),
            capabilities,
            status,
            status_markup(health_kind, record.health.value),
        )
    return table


def downloads_table(tasks: Sequence[DownloadTask]) -> Table:
    """Ready for Phase 5 — renders whatever DownloadTasks it's given."""
    return build_table(
        "Downloads",
        ("ID", "Media", "Episode", "Status", "Progress", "Destination"),
        (
            (t.id, t.media_id, t.episode, t.status.value, f"{t.progress:.0%}", t.destination)
            for t in tasks
        ),
        justify=("left", "left", "right", "left", "right", "left"),
    )


def library_table(entries: Sequence[LibraryEntry]) -> Table:
    """Ready for Phase 6."""
    return build_table(
        "Library",
        ("Title", "Favorite", "Last episode", "Plugin"),
        (
            (
                e.title,
                status_markup("success", "yes") if e.is_favorite else "",
                e.last_episode if e.last_episode is not None else "—",
                e.plugin_used or "—",
            )
            for e in entries
        ),
        justify=("left", "left", "right", "left"),
    )


def history_table(entries: Sequence[HistoryEntry]) -> Table:
    """Ready for Phase 6."""
    return build_table(
        "History",
        ("Title", "Episode", "Event", "Plugin"),
        ((e.title, e.episode, e.event, e.plugin_used or "—") for e in entries),
        justify=("left", "right", "left", "left"),
        sort_key=lambda row: row[0],
    )


def metadata_table(items: Sequence[MediaItem]) -> Table:
    """Ready for Phase 4 — one row per normalized search result."""
    return build_table(
        "Results",
        ("Title", "Year", "Episodes", "Sources"),
        (
            (
                item.title,
                item.year if item.year is not None else "—",
                item.episode_count if item.episode_count is not None else "—",
                ", ".join(item.source_plugins) or "—",
            )
            for item in items
        ),
        justify=("left", "right", "right", "left"),
    )

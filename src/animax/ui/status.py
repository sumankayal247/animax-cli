"""Reusable status-indicator rendering: ✓ ✗ ⚠ ℹ ○, with ASCII fallback."""

from __future__ import annotations

from typing import Literal

from rich.text import Text

from animax.ui.renderers import styles
from animax.ui.renderers.icons import icon

StatusKind = Literal["success", "error", "warning", "info", "pending", "running"]

_STYLE_BY_KIND: dict[StatusKind, str] = {
    "success": styles.SUCCESS,
    "error": styles.ERROR,
    "warning": styles.WARNING,
    "info": styles.INFO,
    "pending": styles.STATUS_PENDING,
    "running": styles.STATUS_RUNNING,
}


def status_text(kind: StatusKind, label: str) -> Text:
    """A single ``<icon> label`` line, colored by kind."""
    style = _STYLE_BY_KIND[kind]
    text = Text()
    text.append(f"{icon(kind)} ", style=style)
    text.append(label, style=style)
    return text


def status_markup(kind: StatusKind, label: str) -> str:
    """The Rich markup string form of status_text — for embedding inside a
    table cell or panel body where a Text object can't be nested directly.
    """
    style = _STYLE_BY_KIND[kind]
    return f"[{style}]{icon(kind)} {label}[/]"

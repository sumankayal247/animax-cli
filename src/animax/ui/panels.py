"""Reusable panels: success/warning/error/info, plus a generic one for
anything else (config sections, plugin details, system info, version/about).
"""

from __future__ import annotations

from rich.panel import Panel

from animax.ui.console import console
from animax.ui.renderers import styles
from animax.ui.renderers.icons import icon


def panel(body: str, *, title: str | None = None, style: str = styles.MUTED) -> Panel:
    """A generic bordered panel. Prefer the semantic helpers below when they fit."""
    return Panel(body, title=title, border_style=style)


def success_panel(body: str, *, title: str = "Success") -> None:
    console.print(Panel(body, title=f"{icon('success')} {title}", border_style=styles.SUCCESS))


def warning_panel(body: str, *, title: str = "Warning") -> None:
    console.print(Panel(body, title=f"{icon('warning')} {title}", border_style=styles.WARNING))


def error_panel(body: str, *, title: str = "Error") -> None:
    console.print(Panel(body, title=f"{icon('error')} {title}", border_style=styles.ERROR))


def info_panel(body: str, *, title: str = "Info") -> None:
    console.print(Panel(body, title=f"{icon('info')} {title}", border_style=styles.INFO))

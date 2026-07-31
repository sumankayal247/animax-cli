"""The shared Rich theme and console instance every CLI command renders through."""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

ANIMAX_THEME = Theme(
    {
        "animax.title": "bold magenta",
        "animax.success": "bold green",
        "animax.warning": "bold yellow",
        "animax.error": "bold red",
        "animax.info": "cyan",
        "animax.muted": "dim",
    }
)

console = Console(theme=ANIMAX_THEME)

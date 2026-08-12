"""The shared Rich Console instance every renderer prints through, and the
one place that reconfigures it (theme, color, width) at startup.

`console` keeps a stable object identity for the life of the process —
`configure_ui()` mutates it in place (`push_theme`, `no_color`) rather
than replacing it, specifically so the many `from animax.ui.theme import
console` bindings taken before configuration runs still see the update
(Python's `from x import y` binds a reference once; reassigning `x.y`
later would NOT be visible through an already-taken `y` binding, but
mutating the object `y` still points to is).
"""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

_DEFAULT_THEME = Theme(
    {
        "animax.title": "bold magenta",
        "animax.accent": "magenta",
        "animax.success": "bold green",
        "animax.warning": "bold yellow",
        "animax.error": "bold red",
        "animax.info": "cyan",
        "animax.muted": "grey62",
    }
)

#: The process-wide console. Safe to import and use before configure_ui()
#: runs (e.g. during early logging setup) — it just renders with the
#: default dark palette and auto-detected color support until configured.
console = Console(theme=_DEFAULT_THEME)

_theme_applied = False


def apply_theme(theme: Theme) -> None:
    """Replace the console's active theme in place (object identity preserved).

    Pops any previously-applied theme first, so calling this repeatedly
    (e.g. across tests in one process) swaps the theme rather than
    growing Rich's internal theme stack indefinitely.
    """
    global _theme_applied
    if _theme_applied:
        console.pop_theme()
    console.push_theme(theme, inherit=False)
    _theme_applied = True


def set_no_color(no_color: bool) -> None:
    console.no_color = no_color


def get_console() -> Console:
    """Explicit accessor, for call sites that prefer a function over a bare import."""
    return console

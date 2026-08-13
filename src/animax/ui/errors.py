"""Renders errors as friendly Rich panels instead of raw tracebacks.

The `__main__` entrypoint is the only place that should ever call these —
everything below it should raise AnimaxError (or let unexpected exceptions
propagate) and trust the top level to present them well.
"""

from __future__ import annotations

from rich.console import Group
from rich.panel import Panel
from rich.traceback import Traceback

from animax.config.paths import log_dir
from animax.core.errors import AnimaxError
from animax.logging_config import log_crash
from animax.ui.theme import console


def render_error(error: AnimaxError, *, debug: bool = False) -> None:
    body = [f"[animax.error]{error.message}[/]"]
    if error.reason:
        body.append(f"[animax.muted]Reason:[/] {error.reason}")
    if error.fix:
        body.append(f"[animax.info]Fix:[/] {error.fix}")
    
    renderables = ["\n\n".join(body)]
    if debug and error.__traceback__:
        renderables.append(Traceback.from_exception(type(error), error, error.__traceback__))
        
    console.print(Panel(Group(*renderables), title="Error", border_style="red"))


def render_unexpected_error(error: Exception) -> None:
    log_crash(error)
    crash_path = log_dir() / "crash.log"
    console.print(
        Panel(
            f"[animax.error]{type(error).__name__}:[/] {error}\n\n"
            f"[animax.muted]This looks like a bug. A crash report was saved to {crash_path}.[/]",
            title="Unexpected error",
            border_style="red",
        )
    )

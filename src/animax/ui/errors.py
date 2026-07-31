"""Renders errors as friendly Rich panels instead of raw tracebacks.

The `__main__` entrypoint is the only place that should ever call these —
everything below it should raise AnimaxError (or let unexpected exceptions
propagate) and trust the top level to present them well.
"""

from __future__ import annotations

from rich.panel import Panel

from animax.core.errors import AnimaxError
from animax.ui.theme import console


def render_error(error: AnimaxError) -> None:
    body = [f"[animax.error]{error.message}[/]"]
    if error.reason:
        body.append(f"[animax.muted]Reason:[/] {error.reason}")
    if error.fix:
        body.append(f"[animax.info]Fix:[/] {error.fix}")
    console.print(Panel("\n\n".join(body), title="Error", border_style="red"))


def render_unexpected_error(error: Exception) -> None:
    console.print(
        Panel(
            f"[animax.error]{type(error).__name__}:[/] {error}\n\n"
            "[animax.muted]This looks like a bug. Please open an issue with the "
            "steps to reproduce, or re-run with --debug for more detail.[/]",
            title="Unexpected error",
            border_style="red",
        )
    )

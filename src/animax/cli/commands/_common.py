"""Shared helper for commands not yet implemented in the current phase."""

from __future__ import annotations

import typer

from animax.ui.theme import console


def not_yet_implemented(command_name: str, phase: str) -> None:
    console.print(
        f"[animax.warning]`{command_name}` isn't implemented yet.[/] "
        f"Planned for {phase} — see docs/Roadmap.md."
    )
    raise typer.Exit(code=0)

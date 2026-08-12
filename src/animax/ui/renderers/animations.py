"""Subtle animation helpers — spinners only, gated by ui.runtime.animations_enabled.

`animations_enabled` is already resolved (in ui.theme.configure_ui) from
--no-animation, config.ui.animations, and capabilities.is_interactive
(never animate in CI or a non-TTY) — this module just honors that
decision, it doesn't re-derive it.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from animax.ui.console import console
from animax.ui.runtime import get_state

#: A restrained spinner — no bouncing/flashy frames, matches the
#: "never flashy" design philosophy.
DEFAULT_SPINNER = "dots"


@contextmanager
def status(message: str, *, spinner: str = DEFAULT_SPINNER) -> Iterator[None]:
    """A spinner while a block runs; a single static line if animations are off."""
    if not get_state().animations_enabled:
        console.print(f"[animax.muted]{message}[/]")
        yield
        return
    with console.status(message, spinner=spinner):
        yield

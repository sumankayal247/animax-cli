"""Startup experience: an optional banner, version line, and environment
summary — the first thing a user sees, gated by config/CLI flags so it
never gets in the way of scripted/CI usage.
"""

from __future__ import annotations

from rich.text import Text

from animax import __version__
from animax.core.constants import APP_NAME
from animax.ui.capabilities import TerminalCapabilities, get_capabilities
from animax.ui.console import console
from animax.ui.renderers.icons import icon
from animax.ui.runtime import get_state

_WORDMARK = r"""
   _          _
  /_\  _ _ (_)_ __  __ ___ __
 / _ \| ' \| | '  \/ _` \ \ /
/_/ \_\_||_|_|_|_|_\__,_/_\_\
""".strip("\n")


def render_banner(*, show_wordmark: bool = True) -> None:
    """Print the startup banner. Respects ascii_mode (drops the wordmark,
    which relies on box-drawing-adjacent characters that read poorly with
    ascii_mode's simplified glyph set) and animations_enabled has no
    bearing here — a banner is static, never animated.
    """
    if show_wordmark and not get_state().ascii_mode:
        # Text(), not an f-string with [markup] — the wordmark's own
        # backslashes can otherwise be parsed as a Rich markup escape
        # (`\[` = literal "[") and break the closing style tag.
        console.print(Text(_WORDMARK, style="animax.title"))
    console.print(f"[animax.title]{APP_NAME}[/] [animax.muted]v{__version__}[/]")


def render_environment_summary(capabilities: TerminalCapabilities | None = None) -> None:
    """A compact "what did we detect" line, useful for `anime doctor` /
    `anime about` and for bug reports.
    """
    caps = capabilities or get_capabilities()
    color = icon("success") if caps.supports_color else icon("warning")
    unicode_ = icon("success") if caps.supports_unicode else icon("warning")
    tty = icon("success") if caps.is_tty else icon("info")
    console.print(
        f"[animax.muted]Terminal:[/] {caps.width}x{caps.height}  "
        f"[animax.muted]Color:[/] {color}  "
        f"[animax.muted]Unicode:[/] {unicode_}  "
        f"[animax.muted]TTY:[/] {tty}  "
        f"[animax.muted]Platform:[/] {caps.platform_name}"
    )

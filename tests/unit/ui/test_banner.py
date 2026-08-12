from __future__ import annotations

from collections.abc import Callable

import animax.ui.banner as banner_module
from animax.ui.banner import render_banner, render_environment_summary
from animax.ui.capabilities import TerminalCapabilities
from animax.ui.runtime import configure


def test_render_banner_shows_version(capture_console: Callable[..., str]) -> None:
    out = capture_console(banner_module, render_banner)
    assert "animax-cli" in out
    assert "v" in out


def test_render_banner_drops_wordmark_in_ascii_mode(capture_console: Callable[..., str]) -> None:
    configure(ascii_mode=True)
    out = capture_console(banner_module, render_banner)
    # The wordmark contains backslash/underscore art; with ascii_mode on,
    # only the plain version line should print.
    assert out.strip().startswith("animax-cli")


def test_render_banner_can_skip_wordmark(capture_console: Callable[..., str]) -> None:
    out = capture_console(banner_module, render_banner, show_wordmark=False)
    assert out.strip().startswith("animax-cli")


def test_render_environment_summary(capture_console: Callable[..., str]) -> None:
    caps = TerminalCapabilities(
        width=120,
        height=40,
        is_tty=True,
        is_ci=False,
        supports_color=True,
        supports_unicode=True,
        platform_name="Linux",
    )
    out = capture_console(banner_module, render_environment_summary, caps)
    assert "120x40" in out
    assert "Linux" in out

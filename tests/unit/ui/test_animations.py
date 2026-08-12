from __future__ import annotations

from collections.abc import Callable

import animax.ui.renderers.animations as animations_module
from animax.ui.renderers.animations import status
from animax.ui.runtime import configure


def test_status_prints_static_line_when_animations_disabled(
    capture_console: Callable[..., str],
) -> None:
    configure(animations_enabled=False)

    def _run() -> None:
        with status("working"):
            pass

    out = capture_console(animations_module, _run)
    assert "working" in out


def test_status_runs_block_when_animations_enabled() -> None:
    configure(animations_enabled=True)
    ran = False
    with status("working"):
        ran = True
    assert ran is True

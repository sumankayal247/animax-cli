from __future__ import annotations

import io
from collections.abc import Callable
from typing import Any

import pytest
from rich.console import Console

from animax.ui.theme import ANIMAX_THEME


@pytest.fixture
def capture_console(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., str]:
    """Redirect a ui module's `console` to an in-memory buffer for one call.

    Each ui module does ``from animax.ui.console import console``, which
    binds its own reference to the shared Console object — patching
    ``animax.ui.console.console`` wouldn't be visible through an
    already-taken binding, so this patches the *consuming* module's name
    instead. Pass one module, or a list when the call under test delegates
    to another ui module too (e.g. errors.py calling panels.error_panel).
    Usage: ``capture_console(panels_module, success_panel, "hi")``.
    """

    def _capture(module: Any, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
        buf = io.StringIO()
        test_console = Console(file=buf, force_terminal=False, width=100, theme=ANIMAX_THEME)
        modules = module if isinstance(module, list) else [module]
        for mod in modules:
            monkeypatch.setattr(mod, "console", test_console)
        fn(*args, **kwargs)
        return buf.getvalue()

    return _capture

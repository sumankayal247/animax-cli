from __future__ import annotations

from animax.ui.renderers.icons import icon
from animax.ui.runtime import configure


def test_unicode_icons_by_default() -> None:
    assert icon("success") == "✓"
    assert icon("error") == "✗"


def test_ascii_fallback_when_ascii_mode_enabled() -> None:
    configure(ascii_mode=True)
    assert icon("success") == "[OK]"
    assert icon("error") == "[X]"


def test_unknown_name_falls_back_to_bullet() -> None:
    assert icon("not-a-real-icon") == icon("bullet")

from __future__ import annotations

from animax.ui.status import status_markup, status_text


def test_status_text_contains_label() -> None:
    text = status_text("success", "all good")
    assert "all good" in text.plain


def test_status_markup_contains_icon_and_label() -> None:
    markup = status_markup("error", "broken")
    assert "broken" in markup
    assert "animax.error" in markup

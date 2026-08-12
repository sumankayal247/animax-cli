from __future__ import annotations

from pathlib import Path

import pytest

from animax.core.errors import UiError
from animax.ui.capabilities import TerminalCapabilities, set_capabilities
from animax.ui.prompts import confirm, multiselect, path_picker, select, text


def _caps(is_tty: bool, is_ci: bool = False) -> TerminalCapabilities:
    return TerminalCapabilities(
        width=100,
        height=24,
        is_tty=is_tty,
        is_ci=is_ci,
        supports_color=True,
        supports_unicode=True,
        platform_name="Linux",
    )


def test_confirm_returns_default_when_not_interactive() -> None:
    set_capabilities(_caps(is_tty=False))
    assert confirm("proceed?", default=True) is True
    assert confirm("proceed?", default=False) is False


def test_text_returns_default_when_not_interactive() -> None:
    set_capabilities(_caps(is_tty=False))
    assert text("name?", default="fallback") == "fallback"


def test_text_raises_without_default_when_not_interactive() -> None:
    set_capabilities(_caps(is_tty=False))
    with pytest.raises(UiError):
        text("name?")


def test_select_returns_first_choice_when_not_interactive() -> None:
    set_capabilities(_caps(is_tty=False))
    assert select("pick one", ["a", "b", "c"]) == "a"


def test_select_raises_on_empty_choices() -> None:
    set_capabilities(_caps(is_tty=True))
    with pytest.raises(UiError):
        select("pick one", [])


def test_multiselect_returns_empty_when_not_interactive() -> None:
    set_capabilities(_caps(is_tty=False))
    assert multiselect("pick some", ["a", "b"]) == []


def test_path_picker_returns_default_when_not_interactive(tmp_path: Path) -> None:
    set_capabilities(_caps(is_tty=False))
    assert path_picker("where?", default=tmp_path) == tmp_path


def test_path_picker_raises_without_default_when_not_interactive() -> None:
    set_capabilities(_caps(is_tty=False))
    with pytest.raises(UiError):
        path_picker("where?")


def test_select_interactive_uses_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    set_capabilities(_caps(is_tty=True))
    monkeypatch.setattr("animax.ui.prompts.IntPrompt.ask", lambda *a, **k: 2)
    assert select("pick one", ["a", "b", "c"]) == "b"


def test_multiselect_interactive_parses_indices(monkeypatch: pytest.MonkeyPatch) -> None:
    set_capabilities(_caps(is_tty=True))
    monkeypatch.setattr("animax.ui.prompts.Prompt.ask", lambda *a, **k: "1,3")
    assert multiselect("pick some", ["a", "b", "c"]) == ["a", "c"]

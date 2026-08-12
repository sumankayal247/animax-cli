from __future__ import annotations

from collections.abc import Callable

import animax.ui.common as common_module
from animax.ui.common import (
    badge,
    bullet_list,
    fatal,
    horizontal_rule,
    info,
    key_value,
    next_steps,
    note,
    section_header,
    success,
    tag,
    tip,
    warning,
)


def test_success(capture_console: Callable[..., str]) -> None:
    assert "done" in capture_console(common_module, success, "done")


def test_warning(capture_console: Callable[..., str]) -> None:
    assert "careful" in capture_console(common_module, warning, "careful")


def test_fatal(capture_console: Callable[..., str]) -> None:
    assert "boom" in capture_console(common_module, fatal, "boom")


def test_info(capture_console: Callable[..., str]) -> None:
    assert "fyi" in capture_console(common_module, info, "fyi")


def test_tip(capture_console: Callable[..., str]) -> None:
    out = capture_console(common_module, tip, "use --debug")
    assert "Tip" in out
    assert "use --debug" in out


def test_note(capture_console: Callable[..., str]) -> None:
    out = capture_console(common_module, note, "heads up")
    assert "Note" in out


def test_next_steps(capture_console: Callable[..., str]) -> None:
    out = capture_console(common_module, next_steps, ["do this", "then that"])
    assert "1." in out
    assert "do this" in out
    assert "2." in out


def test_bullet_list(capture_console: Callable[..., str]) -> None:
    out = capture_console(common_module, bullet_list, ["one", "two"])
    assert "one" in out
    assert "two" in out


def test_key_value_aligns_keys(capture_console: Callable[..., str]) -> None:
    out = capture_console(common_module, key_value, {"short": "1", "longer": "2"})
    assert "short" in out
    assert "longer" in out


def test_key_value_empty_is_a_noop(capture_console: Callable[..., str]) -> None:
    out = capture_console(common_module, key_value, {})
    assert out == ""


def test_horizontal_rule_with_title(capture_console: Callable[..., str]) -> None:
    out = capture_console(common_module, horizontal_rule, "Section")
    assert "Section" in out


def test_section_header(capture_console: Callable[..., str]) -> None:
    out = capture_console(common_module, section_header, "My Section")
    assert "My Section" in out


def test_badge_returns_text_object() -> None:
    result = badge("NEW")
    assert "NEW" in result.plain


def test_tag_returns_markup_string() -> None:
    result = tag("beta")
    assert "beta" in result

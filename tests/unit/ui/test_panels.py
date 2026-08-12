from __future__ import annotations

from collections.abc import Callable

import animax.ui.panels as panels_module
from animax.ui.panels import error_panel, info_panel, panel, success_panel, warning_panel


def test_success_panel_renders_body(capture_console: Callable[..., str]) -> None:
    out = capture_console(panels_module, success_panel, "all good")
    assert "all good" in out
    assert "Success" in out


def test_error_panel_renders_body(capture_console: Callable[..., str]) -> None:
    out = capture_console(panels_module, error_panel, "broke")
    assert "broke" in out


def test_warning_panel_renders_body(capture_console: Callable[..., str]) -> None:
    out = capture_console(panels_module, warning_panel, "careful")
    assert "careful" in out


def test_info_panel_renders_body(capture_console: Callable[..., str]) -> None:
    out = capture_console(panels_module, info_panel, "fyi")
    assert "fyi" in out


def test_generic_panel_builds_object() -> None:
    built = panel("body text", title="Custom")
    assert built.title == "Custom"

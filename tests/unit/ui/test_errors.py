from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

import animax.ui.errors as errors_module
import animax.ui.panels as panels_module
from animax.core.errors import ConfigError
from animax.ui.errors import render_error, render_unexpected_error

_MODULES = [errors_module, panels_module]


def test_render_error_shows_message_reason_fix(capture_console: Callable[..., str]) -> None:
    error = ConfigError("bad config", reason="missing key", fix="add the key")
    out = capture_console(_MODULES, render_error, error)
    assert "bad config" in out
    assert "missing key" in out
    assert "add the key" in out


def test_render_error_debug_includes_traceback(capture_console: Callable[..., str]) -> None:
    try:
        raise ConfigError("bad config")
    except ConfigError as error:
        out = capture_console(_MODULES, render_error, error, debug=True)
    # A traceback frame reference (this test file/function) should appear.
    assert "test_errors" in out


def test_render_unexpected_error_writes_crash_log(
    capture_console: Callable[..., str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("animax.ui.errors.log_dir", lambda: tmp_path)
    monkeypatch.setattr("animax.logging_config.log_dir", lambda: tmp_path)
    error = RuntimeError("boom")
    out = capture_console(_MODULES, render_unexpected_error, error)
    assert "boom" in out
    assert "RuntimeError" in out
    assert (tmp_path / "crash.log").exists()
    assert "boom" in (tmp_path / "crash.log").read_text()

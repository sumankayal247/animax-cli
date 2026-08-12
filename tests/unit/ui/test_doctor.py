from __future__ import annotations

from collections.abc import Callable

import animax.ui.doctor as doctor_module
import animax.ui.panels as panels_module
from animax.installer.checks import CheckResult
from animax.ui.doctor import render_doctor_results

_MODULES = [doctor_module, panels_module]


def test_all_passed_returns_true(capture_console: Callable[..., str]) -> None:
    results = [CheckResult(name="Python", passed=True, detail="3.12")]
    all_passed = None

    def _run() -> None:
        nonlocal all_passed
        all_passed = render_doctor_results(results)

    out = capture_console(_MODULES, _run)
    assert all_passed is True
    assert "Python" in out
    assert "All 1 checks passed" in out


def test_failed_check_shows_recommendation(capture_console: Callable[..., str]) -> None:
    results = [
        CheckResult(name="Database", passed=False, detail="locked", fix="restart the process"),
    ]
    all_passed = None

    def _run() -> None:
        nonlocal all_passed
        all_passed = render_doctor_results(results)

    out = capture_console(_MODULES, _run)
    assert all_passed is False
    assert "restart the process" in out
    assert "Recommendations" in out

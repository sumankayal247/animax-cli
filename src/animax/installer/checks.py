"""Individual, low-level environment/installation checks used by `anime doctor`.

Each check is self-contained and returns a CheckResult rather than raising,
so one failing check never stops the rest from running. Orchestration and
presentation belong to services.doctor_service and ui.doctor, not here.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from animax.config import paths as config_paths
from animax.core.constants import COMMAND_NAME
from animax.database.connection import initialize as initialize_database

MINIMUM_PYTHON_VERSION = (3, 12)


@dataclass(slots=True)
class CheckResult:
    name: str
    passed: bool
    detail: str
    fix: str | None = None


def check_python_version(minimum: tuple[int, int] = MINIMUM_PYTHON_VERSION) -> CheckResult:
    current = sys.version_info[:2]
    passed = current >= minimum
    detail = f"Python {sys.version.split()[0]}"
    fix = None
    if not passed:
        fix = f"Install Python {minimum[0]}.{minimum[1]}+ and re-run `{COMMAND_NAME} doctor`."
    return CheckResult(name="Python version", passed=passed, detail=detail, fix=fix)


def check_directory_writable(name: str, path: Path) -> CheckResult:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".animax_write_test"
        probe.write_text("ok")
        probe.unlink()
        return CheckResult(name=name, passed=True, detail=str(path))
    except OSError as exc:
        return CheckResult(
            name=name,
            passed=False,
            detail=str(path),
            fix=f"Ensure the process can write to {path} ({exc}).",
        )


async def check_database() -> CheckResult:
    target = config_paths.database_file()
    try:
        await initialize_database(target)
        return CheckResult(name="Database", passed=True, detail=str(target))
    except Exception as exc:
        return CheckResult(
            name="Database",
            passed=False,
            detail=str(target),
            fix=f"Could not initialize the database: {exc}",
        )


async def check_plugins() -> CheckResult:
    from animax.services.plugin_service import discover_plugins
    try:
        records, warnings = await discover_plugins()
        if warnings:
            return CheckResult(
                name="Plugin manager",
                passed=False,
                detail=f"{len(records)} loaded, {len(warnings)} warnings",
                fix="Run `anime plugins` to see warnings.",
            )
        return CheckResult(name="Plugin manager", passed=True, detail=f"{len(records)} loaded")
    except Exception as exc:
        return CheckResult(
            name="Plugin manager",
            passed=False,
            detail="Failed to load plugins",
            fix=str(exc),
        )

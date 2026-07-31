"""Orchestrates the installer/ checks for `anime doctor`.

Phase 1 scope: Python version, config/cache/data directory creation and
write permissions, database initialization. Media player availability,
plugin health, network connectivity, and disk space checks are added as
those subsystems land (player/ in Phase 5, plugins in Phase 4, packaging
in Phase 7) — see docs/Roadmap.md.
"""

from __future__ import annotations

from animax.config import paths as config_paths
from animax.installer.checks import (
    CheckResult,
    check_database,
    check_directory_writable,
    check_python_version,
)


async def run_checks() -> list[CheckResult]:
    return [
        check_python_version(),
        check_directory_writable("Config directory", config_paths.config_dir()),
        check_directory_writable("Cache directory", config_paths.cache_dir()),
        check_directory_writable("Data directory", config_paths.data_dir()),
        check_directory_writable("Log directory", config_paths.log_dir()),
        await check_database(),
    ]

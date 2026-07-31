"""Platform-appropriate filesystem locations for config, cache, data, logs.

Backed by platformdirs so behavior is correct on Linux, macOS, and Windows
without any OS-specific branching in the rest of the codebase.
"""

from __future__ import annotations

from pathlib import Path

import platformdirs

from animax.core.constants import APP_NAME, USER_PLUGINS_DIRNAME


def config_dir() -> Path:
    return Path(platformdirs.user_config_dir(APP_NAME, appauthor=False))


def cache_dir() -> Path:
    return Path(platformdirs.user_cache_dir(APP_NAME, appauthor=False))


def data_dir() -> Path:
    return Path(platformdirs.user_data_dir(APP_NAME, appauthor=False))


def log_dir() -> Path:
    return Path(platformdirs.user_log_dir(APP_NAME, appauthor=False))


def config_file() -> Path:
    return config_dir() / "settings.toml"


def database_file() -> Path:
    return data_dir() / "animax.db"


def user_plugin_dir() -> Path:
    return config_dir() / USER_PLUGINS_DIRNAME


def ensure_directories() -> None:
    """Create every managed directory if it doesn't already exist."""
    for directory in (config_dir(), cache_dir(), data_dir(), log_dir(), user_plugin_dir()):
        directory.mkdir(parents=True, exist_ok=True)

"""Load and save Settings as TOML on disk.

Reading uses the stdlib ``tomllib``; writing uses ``tomli_w`` (there is no
stdlib TOML writer). Both operate on plain dicts produced/consumed by
Pydantic, so Settings itself never touches file I/O.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w

from animax.config.paths import config_file
from animax.config.schema import Settings
from animax.core.errors import ConfigError


def load(path: Path | None = None) -> Settings:
    """Load Settings from disk, or return defaults if no file exists yet."""
    target = path or config_file()
    if not target.exists():
        return Settings()

    try:
        with target.open("rb") as fh:
            raw = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(
            f"Config file at {target} is not valid TOML.",
            reason=str(exc),
            fix="Fix the syntax error, or delete the file to regenerate defaults.",
        ) from exc

    try:
        return Settings.model_validate(raw)
    except Exception as exc:
        raise ConfigError(
            f"Config file at {target} failed validation.",
            reason=str(exc),
            fix=(
                "Check docs/Configuration.md for the expected schema, "
                "or delete the file to regenerate defaults."
            ),
        ) from exc


def save(settings: Settings, path: Path | None = None) -> None:
    """Persist Settings to disk as TOML, creating parent directories as needed."""
    target = path or config_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    # TOML has no null literal, so fields left at their None default (e.g.
    # download.directory) are omitted rather than serialized; Settings
    # re-applies the same None default for any key missing on load.
    data = settings.model_dump(mode="json", exclude_none=True)
    with target.open("wb") as fh:
        tomli_w.dump(data, fh)


def ensure_exists(path: Path | None = None) -> Settings:
    """Load Settings, writing fresh defaults to disk first if none exist yet."""
    target = path or config_file()
    if target.exists():
        return load(target)
    settings = Settings()
    save(settings, target)
    return settings

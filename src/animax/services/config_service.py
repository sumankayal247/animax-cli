"""Business logic around loading and resolving configuration."""

from __future__ import annotations

from pathlib import Path

from animax.config.loader import ensure_exists
from animax.config.schema import Settings


def load_settings() -> Settings:
    return ensure_exists()


def resolve_download_directory(settings: Settings, cwd: Path) -> Path:
    """Downloads default to the current working directory unless overridden.

    E.g. running `anime download` from inside ~/Anime downloads there,
    unless download.directory is set in configuration.
    """
    if settings.download.directory:
        return Path(settings.download.directory).expanduser()
    return cwd

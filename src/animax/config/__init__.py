"""Configuration: schema, TOML persistence, and platform-appropriate paths."""

from animax.config.loader import ensure_exists, load, save
from animax.config.schema import (
    CacheConfig,
    DownloadConfig,
    LoggingConfig,
    PlayerConfig,
    PluginsConfig,
    Settings,
)

__all__ = [
    "CacheConfig",
    "DownloadConfig",
    "LoggingConfig",
    "PlayerConfig",
    "PluginsConfig",
    "Settings",
    "ensure_exists",
    "load",
    "save",
]

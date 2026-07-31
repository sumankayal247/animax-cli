"""The configuration schema, as Pydantic Settings models.

``Settings.schema_version`` tracks CONFIG_SCHEMA_VERSION (core.constants /
core.versioning). Bump CONFIG_SCHEMA_VERSION and add a migration in
animax.config.loader whenever a change here is not backward compatible.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from animax.core.constants import CONFIG_SCHEMA_VERSION


class PlayerConfig(BaseModel):
    preferred_order: list[str] = Field(default_factory=lambda: ["mpv", "vlc", "system"])


class DownloadConfig(BaseModel):
    directory: str | None = None
    """Absolute path to download into. None means: use the current working
    directory at launch time (see services.download_service)."""
    concurrent_downloads: int = 3
    retries: int = 3
    timeout_seconds: int = 30


class PluginsConfig(BaseModel):
    disabled: list[str] = Field(default_factory=list)
    priority_overrides: dict[str, int] = Field(default_factory=dict)


class CacheConfig(BaseModel):
    lifetime_seconds: int = 86_400


class LoggingConfig(BaseModel):
    level: str = "INFO"
    debug: bool = False


class Settings(BaseSettings):
    """Root configuration object, loaded from settings.toml and env vars.

    Environment variables use the ANIMAX_ prefix with double-underscore
    nesting, e.g. ANIMAX_DOWNLOAD__CONCURRENT_DOWNLOADS=5.
    """

    model_config = SettingsConfigDict(
        env_prefix="ANIMAX_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    schema_version: str = CONFIG_SCHEMA_VERSION
    theme: str = "default"
    language: str = "en"
    player: PlayerConfig = Field(default_factory=PlayerConfig)
    download: DownloadConfig = Field(default_factory=DownloadConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

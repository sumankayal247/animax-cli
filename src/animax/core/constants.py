"""Application-wide constants."""

from __future__ import annotations

APP_NAME = "animax-cli"
COMMAND_NAME = "anime"

#: Version of the plugin interface contract. Plugins declare which
#: PLUGIN_API_VERSION they were built against; the plugin manager uses
#: SemVer compatibility rules (see core.versioning) to decide whether a
#: plugin may be loaded.
PLUGIN_API_VERSION = "1.0.0"

#: Version of the on-disk configuration file schema (config/settings.toml).
#: Bump this whenever the config schema changes in a backward-incompatible
#: way, and add a migration in animax.config.migrations.
CONFIG_SCHEMA_VERSION = "1.0.0"

#: Entry-point group that third-party, pip-installed plugins register under.
PLUGIN_ENTRY_POINT_GROUP = "animax.plugins"

#: Sub-directories created under the user config directory.
USER_PLUGINS_DIRNAME = "plugins"

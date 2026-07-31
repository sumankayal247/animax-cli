# Configuration

## Location

Platform-appropriate directories via `platformdirs` (`config/paths.py`):

| Purpose        | Function                    |
|-----------------|------------------------------|
| Config file     | `config_file()` → `config_dir()/settings.toml` |
| Cache            | `cache_dir()`                |
| Data (database)  | `data_dir()`                 |
| Logs             | `log_dir()`                  |
| User plugins     | `user_plugin_dir()` → `config_dir()/plugins/` |

Run `anime config path` to print the resolved config file path for your
platform.

## Format

TOML, validated by a Pydantic Settings model (`config/schema.py:Settings`).
Environment variables override file values with an `ANIMAX_` prefix and
`__` nesting, e.g. `ANIMAX_DOWNLOAD__CONCURRENT_DOWNLOADS=5`.

## Schema (`Settings`, `CONFIG_SCHEMA_VERSION = "1.0.0"`)

```toml
schema_version = "1.0.0"
theme = "default"
language = "en"

[player]
preferred_order = ["mpv", "vlc", "system"]

[download]
directory = null          # null = use the current working directory
concurrent_downloads = 3
retries = 3
timeout_seconds = 30

[plugins]
disabled = []
priority_overrides = {}

[cache]
lifetime_seconds = 86400

[logging]
level = "INFO"
debug = false
```

## Loading

`config.loader.ensure_exists()` loads `settings.toml`, writing fresh
defaults to disk on first run if it doesn't exist. A malformed or
schema-invalid file raises `core.errors.ConfigError` with a friendly
message (never a raw traceback) — see `ui/errors.py`.

## Schema evolution

Bump `CONFIG_SCHEMA_VERSION` in `core/constants.py` and add a migration
step to `config/loader.py` whenever a change is not backward compatible.
There is only one version so far.

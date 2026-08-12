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
theme = "auto"            # "auto" | "light" | "dark" | "ansi"
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

[ui]
accent_color = null       # e.g. "blue" — overrides the theme's default accent
ascii_mode = null         # null = auto-detect from terminal capabilities
animations = true         # master switch; still off in CI/non-TTY regardless
banner = true              # startup wordmark on `anime about`
```

`theme` accepts an old value from before Phase 3 too — a config file with
`theme = "default"` (the pre-Phase-3 default) still loads fine and is
treated the same as `"auto"` at resolution time
(`ui.theme.resolve_theme_name`), not rejected. `--no-color`, `--ascii`,
and `--no-animation` are CLI flags that always override whatever `ui.*`
says for that one run. See docs/Architecture.md "UI framework (Phase 3)".

## Loading

`config.loader.ensure_exists()` loads `settings.toml`, writing fresh
defaults to disk on first run if it doesn't exist. A malformed or
schema-invalid file raises `core.errors.ConfigError` with a friendly
message (never a raw traceback) — see `ui/errors.py`.

## Schema evolution

Bump `CONFIG_SCHEMA_VERSION` in `core/constants.py` and add a migration
step to `config/loader.py` whenever a change is not backward compatible.
There is only one version so far.

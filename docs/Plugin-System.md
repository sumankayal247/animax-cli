# Plugin System

## Categories and interfaces

| Category       | ABC (`core/interfaces/`)         | Purpose                                   |
|----------------|-----------------------------------|--------------------------------------------|
| Metadata       | `metadata.MetadataPlugin`         | "What is this title" (AniList, MAL, ...)   |
| Search         | `search.SearchPlugin`             | "Where can I get episodes of this title"   |
| Download       | `download.DownloadPlugin`         | Resolve a downloadable file source         |
| Streaming      | `streaming.StreamingPlugin`       | Resolve a direct-play source               |
| Player         | `player.PlayerPlugin`             | Launch a local player (mpv, VLC, ...)      |
| Notification   | `notification.NotificationPlugin` | Deliver a notification                     |
| Authentication | `authentication.AuthenticationPlugin` | Login/session handling for a provider  |

Every plugin implements `core.interfaces.base.BasePlugin`:

- `info` (property, required) — a `models.plugin.PluginInfo`: name, version,
  author, description, category, `api_version`, priority, capabilities.
- `setup()` / `teardown()` (optional, async, default no-op) — lifecycle hooks.
- `health_check()` (optional, async, default: healthy) — used by
  `PluginManager.health_check_all()` and surfaced in `anime plugins`.

Plus whatever abstract methods its category interface adds (e.g.
`MetadataPlugin.search()` / `.get_details()`).

## Load order

1. **Built-in** — discovered by walking `src/animax/plugins/**` (directory
   scan of the bundled package).
2. **User** — directory-scanned from the user plugin directory
   (`anime config path` shows where; single-file plugins, no packaging
   required).
3. **Entry-point** — pip-installed packages registering under the
   `animax.plugins` entry-point group, discovered via
   `importlib.metadata.entry_points()`.

A later source **overrides** an earlier one on a name collision. The
overridden plugin is never silently dropped — it's kept in the registry
disabled, with `shadowed_by` set to the winner's name, and a warning is
logged and surfaced by `anime plugins`.

## Validation

On registration, `PluginManager` checks:

1. The plugin actually implements the interface matching the category it
   declares (`isinstance(instance, CATEGORY_INTERFACES[category])`).
2. Its declared `api_version` is SemVer-compatible (same MAJOR) with the
   app's `PLUGIN_API_VERSION`.

A plugin that fails either check is rejected with a warning, not a crash.
A plugin whose `.info` property or constructor raises is caught, logged,
and skipped the same way — **one broken plugin can never take down the
application.**

## Priority and enable/disable

`PluginManager.enabled(category=...)` returns enabled plugins for a
category sorted by `PluginInfo.priority` (lower = tried first — e.g. for
search aggregation, ranking, or player selection order).
`PluginManager.enable(name)` / `.disable(name)` toggle a plugin at
runtime.

## Writing a plugin

See `src/animax/plugins/unknown_providers.txt` for the full contributor
checklist (which interface to implement, where the file goes, how to
register and test it) and [Provider-API.md](Provider-API.md) for the
per-category method contracts.

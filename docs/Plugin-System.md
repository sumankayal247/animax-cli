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

## Plugin lifecycle

```
Discover ─▶ Import ─▶ Instantiate ─▶ Validate ─▶ Setup ─▶ Health Check ─▶ Ready ─▶ Use ─▶ Teardown
```

Mapped to actual code, and honest about what's wired versus declared:

| Stage | Implemented by | Status |
|---|---|---|
| Discover | `PluginManager._discover_builtin` / `_discover_user_dir` / `_discover_entry_points` | ✅ wired |
| Import | `importlib.import_module` / `importlib.util.spec_from_file_location` / `entry_point.load()` inside the discover methods above | ✅ wired |
| Instantiate | `PluginManager._instantiate` (`plugin_cls()`) | ✅ wired |
| Validate | `PluginManager._validate` (interface + `PLUGIN_API_VERSION` check) | ✅ wired — see "Validation" below |
| Setup | `BasePlugin.setup()` | ⚠️ **declared on the interface, not yet called by `PluginManager`.** A plugin can override it, but nothing invokes it today. Wiring `await instance.setup()` into `_register()` right after a successful registration is tracked in [Roadmap.md](Roadmap.md) Phase 2. |
| Health Check | `BasePlugin.health_check()`, `PluginManager.health_check_all()` | ✅ wired — publishes `ProviderHealthChangedEvent` on change |
| Ready | (implicit) — a `PluginRecord` in the registry with `enabled=True` | ✅ — this is just the state after Validate succeeds |
| Use | `PluginManager.enabled(category=...)`, called by a service | ✅ wired for discovery; no service calls a plugin's category methods yet (Phase 4/5) |
| Teardown | `BasePlugin.teardown()` | ⚠️ **declared, not yet called.** No `PluginManager.shutdown()` exists yet, and the CLI has no process-exit hook to call it from — today's plugin-touching commands (`plugins`, `doctor`) are read-only and short-lived, so nothing holds a resource that needs releasing yet. Tracked alongside Setup in Phase 2. |

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

## Concurrency rules (Phase 4 target — not built yet)

**Yes: multiple providers of the same category run concurrently**, once
a service actually calls out to them (nothing does yet — `enabled()`
today only returns the list, it doesn't call anyone). The intended shape:

```
services.metadata_service (or search_service)
        │
        │  for each enabled plugin in PluginManager.enabled("metadata"):
        ▼
   asyncio.TaskGroup (or asyncio.gather(..., return_exceptions=True))
        │
        ├─▶ AniListPlugin.search(query)   ─┐
        ├─▶ MALPlugin.search(query)        ├─ concurrent
        └─▶ KitsuPlugin.search(query)     ─┘
        │
        ▼
      merge results (see Architecture.md "Normalization ownership")
```

Each task is wrapped so one plugin's exception doesn't cancel the whole
group and doesn't propagate to the caller — same error-isolation
principle as plugin discovery (see "Validation" above), just applied at
call time instead of load time. See "Failure isolation in aggregation"
below.

## Timeout and retry policy (architecture, not implementation yet)

Every provider call a service makes should eventually be bounded by:

- **Timeout** — a per-call deadline, so one slow provider can't hang a
  search/download indefinitely.
- **Retry with bounded backoff** — transient failures (a dropped
  connection, a 503) get a small number of retries, not an infinite loop.
- **Max concurrent requests** — a cap (e.g. `asyncio.Semaphore`) on how
  many in-flight requests one provider (or the app as a whole) allows at
  once, so aggregating across many enabled plugins can't accidentally
  hammer a single slow provider or exhaust local file descriptors.

None of this is implemented yet — there's no code to point to, unlike
the rest of this document. `config.schema.DownloadConfig` already has
`timeout_seconds`/`retries` fields, but scoped to the download engine
specifically; whether metadata/search calls reuse those or get their own
`providers.*` config section is a Phase 4 decision, made once real
plugins reveal what actually needs tuning independently. Recorded here so
the policy isn't invented ad hoc, plugin by plugin, later.

## Failure isolation in aggregation

Already true at **discovery time** (see "Validation" above): a plugin
that fails to import, instantiate, or validate never stops other plugins
from loading. The same principle applies at **call time**, once services
actually call plugins (Phase 4/5) — explicitly:

**One provider timing out or erroring is not the same as the whole
search/download failing.** A partial result set is the expected, correct
outcome — not a degraded one:

```
Metadata providers:
  AniList     ✔
  MAL         ✔
  Kitsu       ⏱ timeout — excluded, warning logged, doesn't block the rest

→ anime search still returns AniList + MAL results.
```

This is the same shape `anime doctor`'s "Plugin manager" check already
uses today: a rejected/failed plugin is a warning attached to the
result, never a hard failure of the whole operation (see
[Installer.md](Installer.md)). Phase 4's `search_service` /
`metadata_service` apply the identical rule to per-call failures, not
just load-time ones.

## One manager per process, and events

`PluginManager` is a process-wide singleton
(`services.plugin_service.get_plugin_manager()`); discovery
(`load_all()`) runs once and is cached, so multiple commands/services in
the same process share one registry instead of each re-discovering and
re-instantiating every plugin. Call `reload()` to force a fresh pass.

Registration and health checks publish typed events on `core.events`
(`ProviderLoadedEvent`, `ProviderRejectedEvent`, `ProviderHealthChangedEvent`
— see `core/events/plugin_events.py`) rather than calling back into any
specific subscriber directly. See docs/Architecture.md "Events" and
"Plugin Manager: singleton, not per-call".

## Writing a plugin

See `src/animax/plugins/unknown_providers.txt` for the full contributor
checklist (which interface to implement, where the file goes, how to
register and test it) and [Provider-API.md](Provider-API.md) for the
per-category method contracts.

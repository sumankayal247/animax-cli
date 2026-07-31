# Architecture

## Principle

The core application knows nothing about individual content providers. It talks
only to the **Plugin Manager**, which discovers, validates, and exposes plugins
through abstract interfaces (`core/interfaces/`). Nothing outside
`src/animax/plugins/*` should ever import a provider-specific type.

## Layers

```
cli/         Typer commands — thin controllers only. Parse args, call a
             service, render the result with ui/. No business logic.
services/    All business logic. Orchestrates core/, config/, database/,
             cache/, download/, library/, player/, installer/, and plugins
             (via core.plugin_manager) to fulfil a use case.
core/        Framework: plugin interfaces, the plugin manager, the event
             bus, shared errors, SemVer helpers, constants. Depends on
             models/ only — never on services/, cli/, or plugins/.
models/      Shared Pydantic domain models (MediaItem, Episode, DownloadTask,
             PluginInfo/PluginRecord, LibraryEntry, ...). The common
             vocabulary every other layer speaks.
config/      Settings schema (Pydantic Settings), TOML load/save,
             platformdirs-based path resolution.
database/    SQLite schema + aiosqlite connection handling.
cache/       Namespaced, TTL-based on-disk cache.
download/    Generic download engine (queue/retry/resume) — provider-agnostic.
library/     Watch history, favorites, resume state (built on database/).
player/      Local player detection and launch (mpv/VLC/system default).
installer/   Low-level environment/installation checks (`anime doctor`).
plugins/     Concrete plugin implementations, one subpackage per category.
ui/          Rich theme, console, and render functions. cli/ calls into
             ui/ to display results; ui/ never contains business logic.
```

## Dependency direction

```
plugins/  ──depends on──>  core/interfaces, models/
services/ ──depends on──>  core/, models/, config/, database/, cache/,
                            download/, library/, player/, installer/
cli/      ──depends on──>  services/, ui/
ui/       ──depends on──>  models/ (for typed render inputs only)
core/     ──depends on──>  models/  (never on services/, cli/, or plugins/)
```

If you find yourself importing `animax.plugins.*` from `core/` or
`services/`, stop — that's the dependency direction the whole plugin system
exists to prevent. Talk to `core.plugin_manager.PluginManager` instead.

## Plugin load order

See [Plugin-System.md](Plugin-System.md#load-order).

## Request flow

The call chain for every command, once real command logic lands (currently
only `doctor`, `plugins`, and `config show/path` do real work — see
[CLI-Commands.md](CLI-Commands.md)):

```
   CLI
    │   cli/commands/*.py — parse args, call one service function,
    │   render the result with ui/. No business logic.
    ▼
 Services
    │   services/*.py — orchestrates config/, database/, cache/,
    │   download/, library/, player/, installer/, and plugins.
    ▼
Plugin Manager
    │   core/plugin_manager.py — discovers, validates, and exposes
    │   plugins through the ABCs in core/interfaces/. Nothing above
    │   this line ever imports a concrete plugin class directly.
    ▼
 Plugins
     src/animax/plugins/**/*.py — one concrete implementation per
     provider, each satisfying a core/interfaces/ ABC.
```

Each arrow is a one-way dependency: `cli` imports `services`, `services`
imports `core.plugin_manager`, `plugin_manager` imports `core.interfaces` —
but `core/` and `services/` never import from `plugins/`, and `plugins/`
never imports from `services/` or `cli/`. See "Dependency direction" above
and "Import graph" below for how this is enforced/verified in practice.

### Import graph — verified, no runtime cycles

Checked by statically parsing every `import`/`from` in `src/animax/` and
by directly importing the full module graph in both possible orders
(`uv run python -c "import animax.cli.app"` and friends). Result: **no
circular imports at runtime.**

One edge looks like a cycle in a naive static scan but isn't one in
practice: `models/plugin.py` references `core.interfaces.base.BasePlugin`
for a type hint (`PluginRecord.plugin -> BasePlugin`), while
`core/interfaces/base.py` imports `models.plugin.PluginInfo` for real, at
runtime. The `models/plugin.py` side avoids the real cycle by importing
`BasePlugin` only under `if TYPE_CHECKING:` — it's never evaluated at
import time, only by type checkers. This is the standard pattern for a
models module that needs to type-hint something one layer up (`core/`)
without creating a load-time dependency on it; `models/` still only
depends on `core/` for a type-only annotation, never for behavior.

## Public API vs. internal implementation

What plugin authors and contributors can depend on staying stable versus
what's free to change without notice:

| Module | Status | Notes |
|---|---|---|
| `core.interfaces.*` (all ABCs) | **Public** | The plugin contract. Gated by `PLUGIN_API_VERSION`. |
| `models.*` | **Public** | Shared data shapes plugins accept/return. |
| `core.errors.*` | **Public** | Exception types plugins should raise across the interface boundary. |
| `core.constants.PLUGIN_API_VERSION` | **Public** | What a plugin's `PluginInfo.api_version` is checked against. |
| `core.versioning` | **Public** | SemVer parse/compatibility helpers, usable by plugin authors. |
| the `animax.plugins` entry-point group | **Public** | How third-party PyPI plugins register themselves. |
| `anime` CLI surface (commands/flags) | **Public** (user-facing) | Follows the app's own SemVer, not `PLUGIN_API_VERSION`. |
| `cli.*` | Internal | Typer wiring; plugins/contributors never import this. |
| `services.*` | Internal | Business logic, reachable only from `cli/`. Plugins never call into `services/` — they only implement `core.interfaces` and are called *by* `core.plugin_manager`. |
| `core.plugin_manager` | Internal | Plugins are managed by it; they don't import it. |
| `core.events.*` | Internal (for now) | See "Events" below — not yet part of the plugin contract. |
| `config.*`, `database.*`, `cache.*`, `installer.*`, `ui.*`, `logging_config` | Internal | Implementation details of specific subsystems. |
| `plugins.unknown_providers.txt` | Internal, non-code | Dev planning file; never imported or read by the app. |

Rule of thumb: if it's under `core/interfaces/`, `models/`, or
`core/errors.py`, it's part of the contract and changes there are
breaking (bump `PLUGIN_API_VERSION`'s major). Everything else can be
refactored freely as long as the public surface's behavior doesn't
change.

## Startup behavior

**The CLI eagerly imports every command module at process start.**
`cli/app.py` module-level code imports all 16 `cli.commands.*` modules
(`search`, `info`, ..., `diagnose`) and calls `.register(app)` on each,
before any command runs — there is no lazy/deferred import per
subcommand. At Phase 1 scale this is negligible (command modules are
thin and import only `typer` + one or two `services`/`ui` functions each),
but it's worth knowing: every `anime <anything>` invocation currently pays
the import cost of all 16 command modules, not just the one invoked. If
that ever becomes measurable (e.g. once `search`/`download` pull in
heavier plugin/HTTP machinery at import time), the fix is Typer's lazy
subcommand loading (deferring each module's import into its `register`
callback or a `LazyGroup`-style pattern) — not yet needed, so not built.

## Plugin instantiation timing

**Plugins are instantiated eagerly relative to each other, but lazily
relative to CLI startup.** `PluginManager.load_all()` discovers *and*
instantiates every plugin it finds in one pass (there is no
per-plugin/per-category deferral — the whole built-in → user →
entry-point sweep runs immediately when called). However, `load_all()`
itself is not called anywhere during CLI startup (`cli/app.py`'s
module-level code and root callback never touch the plugin manager) — it
only runs when a command that needs it calls
`services.plugin_service.discover_plugins()`, which today is just the
`anime plugins` command. So: running `anime version` never instantiates a
single plugin; running `anime plugins` instantiates *all* of them, every
time, with no caching between commands (each CLI invocation is a fresh
process, so there's nothing to cache within — but Phase 4/5 commands like
`search`/`download` will each independently call `discover_plugins()`
too unless a shared, longer-lived `PluginManager` is introduced then;
flagged in [Roadmap.md](Roadmap.md) as a Phase 4 design question, not
solved now since only one command needs it today).

## Events

**Implemented**, not deferred — `core/events/` is a minimal async
pub/sub bus (`core.events.default_bus`, `core.events.EventBus`) with a
documented event-name catalogue in `core/events/types.py`
(`PLUGIN_LOADED`, `DOWNLOAD_PROGRESS`, etc.). It exists today; what
doesn't exist yet is anything actually publishing to it — `plugin_manager`
doesn't currently call `default_bus.publish(...)` on load/health-change,
and there's no download engine yet to publish progress. Wiring
`core.plugin_manager` to publish `PLUGIN_LOADED`/`PLUGIN_HEALTH_CHANGED`
is a small, natural Phase 2 follow-up; `DOWNLOAD_*` events get their
first real publisher when `download/` is built in Phase 5, consumed by a
Rich `Live` progress view in `ui/`. The bus itself needs no changes for
either — it's already generic pub/sub with error-isolated handlers.

## Versioning

Three independent SemVer numbers are tracked from day one
(`core/versioning.py`, `core/constants.py`):

- **App version** (`animax.__version__`).
- **Plugin API version** (`PLUGIN_API_VERSION`, currently `"1.0.0"`) —
  **already implemented**, not just planned. Every plugin declares the
  version it targets in `PluginInfo.api_version`;
  `PluginManager._validate()` calls `core.versioning.is_compatible()` and
  rejects (logs + skips, doesn't crash) any plugin whose major version
  doesn't match the app's `PLUGIN_API_VERSION`. Covered by
  `tests/unit/test_plugin_manager.py::test_register_rejects_incompatible_api_version`.
- **Config schema version** (`CONFIG_SCHEMA_VERSION`, currently
  `"1.0.0"`) — the field exists on `Settings.schema_version` and is
  persisted to/read from `settings.toml`, but as of Phase 1 nothing
  actually *compares* the file's `schema_version` against the constant or
  runs a migration — `config.loader.load()` just validates the file
  against the current `Settings` shape. That's intentionally the whole
  story for now: there is only one schema version, so there is nothing to
  migrate *from*. The field is there so the first breaking change has
  something to check against; the compatibility-check/migration logic
  itself is a `config/loader.py` addition for whenever
  `CONFIG_SCHEMA_VERSION` is first bumped (tracked in
  [Roadmap.md](Roadmap.md) Phase 2, alongside the rest of core-framework
  hardening).

## Status

Phase 1 (bootstrap). `core/`, `models/`, `config/`, `database/`, `cache/`,
`installer/`, the plugin manager, and the CLI skeleton are implemented.
`download/`, `library/`, `player/`, and all concrete plugins are
placeholders pending Phase 4/5/6.

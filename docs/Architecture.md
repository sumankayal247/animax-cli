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
ui/          A full reusable Rich component library (theme, tables, panels,
             progress, prompts, menus, help, errors — see "UI framework"
             below). cli/ calls into ui/ to display results; ui/ never
             contains business logic.
```

## Service responsibilities

The layer diagram above says `services/` owns "all business logic" — this
is what that means per service, so boundaries don't drift as more get
added. **Implemented today:**

- **`config_service`** — load/resolve `Settings` (`load_settings()`);
  resolve the effective download directory from config + CWD
  (`resolve_download_directory()`).
- **`doctor_service`** — orchestrate `installer.checks` into the
  `anime doctor` report; owns which checks exist and in what order, not
  the checks' own logic.
- **`plugin_service`** — own the process-wide `PluginManager` singleton
  (`get_plugin_manager()`/`reset_plugin_manager()`); expose
  `discover_plugins()` as the one path anything reaches plugins through.

**Planned, named now so future contributors build in the right place**
(none of these exist yet — see [Roadmap.md](Roadmap.md) for when):

- **`search_service`** (Phase 4) — search orchestration end to end: ask
  `metadata_service` for normalized candidates, ask enabled `SearchPlugin`s
  for availability per candidate, merge availability results across
  providers, rank the final list. Does **not** own metadata normalization
  — see "Normalization ownership" below.
- **`metadata_service`** (Phase 4) — metadata aggregation: call every
  enabled `MetadataPlugin`, merge/deduplicate results for the same title
  across providers, own the metadata-service-level cache namespace. Owns
  normalization (see below).
- **`download_service`** (Phase 5) — queue management, resume, retry,
  verification; the business-logic face of the `download/` engine. Owns
  deciding *when* to retry/resume, not the low-level transfer mechanics
  (that's `download/`).
- **`library_service`** (Phase 6) — history, favorites, resume position;
  the business-logic face of `library/` + `database/`.
- **`player_service`** (Phase 5) — player selection/detection ordering
  (`player.preferred_order`), launch orchestration; the business-logic
  face of `player/`.

Rule of thumb for where new logic belongs: if it decides *what* should
happen (which plugins to call, how to merge/rank/retry their results,
what counts as a cache hit), it's a service. If it *does* the mechanical
work once told (a single HTTP request, a single file write, launching one
player process), it belongs one layer down, in the subsystem the service
orchestrates (`core.plugin_manager`, `download/`, `player/`, `database/`).

## Async policy

**Core rule: all network I/O is async.** Every plugin category interface
(`core/interfaces/`) declares its provider-facing methods `async def`;
implementations must use `httpx.AsyncClient`, never a blocking HTTP call
— already stated as a hard rule in
[Provider-API.md](Provider-API.md#rules) ("never block the event loop").

**Filesystem access may be sync unless profiling shows otherwise.**
Reflecting what's already true in the codebase: `config/loader.py` (TOML
read/write) and `cache/store.py` (JSON read/write) use plain
`pathlib`/blocking I/O — deliberately, since local-disk config/cache
reads are fast, happen at most once or twice per CLI invocation, and
making them async would add `asyncio` ceremony (an event loop, `aiofiles`
or a thread-pool wrapper) with no measured benefit. `database/` is the
one exception that's already async (`aiosqlite`) despite being local
disk, because SQLite operations can block on write locks under
concurrent access, and the download engine (Phase 5) will read/write the
database from multiple concurrent tasks.

**Plugins must never block the event loop.** No `time.sleep`, no
`requests`, no synchronous file I/O inside an `async def` plugin method
without a thread-pool wrapper (`asyncio.to_thread`) — a blocking call
inside one plugin's coroutine stalls every other concurrently-running
plugin call sharing that event loop (see "Concurrency rules" in
[Plugin-System.md](Plugin-System.md)), not just its own.

If profiling ever shows a sync filesystem call as a real bottleneck
(large cache directories, frequent config writes under load), that's the
trigger to revisit — not a guess made in advance.

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

## Normalization ownership

Who turns `"ONE PIECE"` / `"One Piece (TV)"` / `"One Piece (1999)"` into
one canonical `MediaItem`? Per the project spec's own Search Flow (query
metadata plugins → merge duplicates → normalize names → ask
search/download plugins → merge → rank → display), this splits into two
distinct jobs, owned one layer apart:

1. **Plugin → `MetadataService`, per-provider translation.** Each
   `MetadataPlugin` already must return `animax.models.*` types, never a
   provider-native shape ([Provider-API.md](Provider-API.md#rules)) — so
   a plugin returns *its own provider's* title/year/etc. as-is, making no
   attempt to match another provider's spelling.
2. **`MetadataService`, cross-provider normalization (owns it).** When
   the same query returns candidates from multiple metadata plugins,
   `metadata_service` is what decides they're the same title (fuzzy title
   match + year proximity), picks/merges canonical fields (e.g. prefer
   the highest-priority plugin's title, keep the rest as `alt_titles`),
   and returns one deduplicated, normalized `MediaItem` list. This is
   steps 1–3 of the Search Flow.

**`SearchService` and `PluginManager` do not own normalization.**
`SearchService` (steps 4–6: ask `SearchPlugin`s for availability, merge
those results, rank) consumes `metadata_service`'s already-normalized
`MediaItem`s — it never re-normalizes a title itself. `PluginManager`
never touches title text at all; its job stops at discovering, validating,
and handing back plugin instances.

## Cache ownership

Two cache layers, different owners, same `cache.Cache` primitive
(namespaced, TTL-based — already implemented, see
[Configuration.md](Configuration.md#format) for `cache.lifetime_seconds`):

```
SearchService / MetadataService
        │  cache.get(f"search:{query}") — service-level cache of
        │  merged/normalized/ranked results, keyed by the resolved
        │  query. This is the cache a repeated `anime search` call hits.
        ▼
    (miss)
        │
        ▼
     PluginManager.enabled("metadata"/"search")
        │
        ▼
      Provider (plugin)
        │  a plugin MAY keep its own Cache(namespace=plugin_name) of
        │  raw provider responses, to avoid rate limits — its own
        │  choice, invisible to the service layer above.
        ▼
   Refresh TTL (cache.lifetime_seconds, per-namespace override)
```

**The service layer owns invalidation policy** for the cache a user's
result actually comes from: `metadata_service`/`search_service` decide
the TTL and when to bypass the cache (e.g. a future `--refresh` flag).
**A plugin may optionally run its own cache** of raw provider responses
under its own namespace — that's an internal optimization for the
plugin's own network efficiency, not something any service reads or
invalidates on its behalf. Neither `core.plugin_manager` nor `cli/`
touches cache directly; only the service layer and, optionally, plugins
themselves do.

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

### Sequence: `anime search "One Piece"` (Phase 4)

The layer diagram above is the general shape; here's one concrete
end-to-end sequence through it, combining "Service responsibilities",
"Normalization ownership", and "Cache ownership" above into what a real
command execution looks like now that Phase 4 has landed:

```
CLI (cli/commands/search.py)
 │  anime search "One Piece"
 ▼
SearchService.search(query)
 │
 ├─▶ MetadataService.resolve(query)
 │     │
 │     ├─▶ cache.get(f"metadata:{query}")  ── hit? return cached MediaItem list
 │     │
 │     ├─▶ (miss) PluginManager.enabled("metadata")
 │     │     ├─▶ AniListPlugin.search(query)   ─┐
 │     │     ├─▶ MALPlugin.search(query)        ├─ concurrent, isolated
 │     │     └─▶ KitsuPlugin.search(query)     ─┘  (see Plugin-System.md
 │     │                                            "Concurrency rules")
 │     │
 │     ├─▶ merge + normalize (dedupe "ONE PIECE" / "One Piece (TV)" / ...)
 │     └─▶ cache.set(f"metadata:{query}", result)
 │
 │  ◀── normalized MediaItem[]
 │
 ├─▶ for each MediaItem: PluginManager.enabled("search")
 │     ├─▶ ProviderA.find(item)   ─┐
 │     └─▶ ProviderB.find(item)   ─┘ concurrent, isolated
 │
 ├─▶ merge availability results across providers
 ├─▶ rank (priority, match score, availability)
 ▼
CLI renders via ui/ (Rich table)
```

Every arrow inside `MetadataService`/`SearchService` above is business
logic (`services/`); every arrow into a named plugin is
`core.plugin_manager` handing back a `core.interfaces` call, per
"Dependency direction". A provider timing out at either concurrent step
doesn't abort the sequence — see
[Plugin-System.md](Plugin-System.md#failure-isolation-in-aggregation).

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
| `core.events.*` | Internal (for now) | Bus and event dataclasses are implemented and wired (see "Events" below), but plugins have no way to subscribe yet — there's no hook mechanism handing plugins a bus reference. Becomes part of the public contract alongside Hook Points (see "Deferred designs" below). |
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

## Plugin Manager: singleton, not per-call

`PluginManager` is a **process-wide singleton**, built by
`services.plugin_service.get_plugin_manager()` and cached at module
level. `discover_plugins()` calls `get_plugin_manager()` then
`manager.load_all()` — and `load_all()` is now idempotent: the first call
runs the full built-in → user → entry-point discovery/instantiation
sweep, every subsequent call in the same process just returns the cached
result. Call `manager.reload()` to force a fresh pass (the "hot-pluggable"
hook — e.g. after installing a plugin at runtime).

This replaces the earlier design where each caller built its own
`PluginManager` and re-ran discovery from scratch. Concretely: today
`anime plugins` is the only caller, so within one CLI invocation nothing
changes observably — but Phase 4/5's `search`/`download` commands will
each need plugins too, and because they go through the same
`get_plugin_manager()` singleton, they now share one registry and one
discovery pass instead of each re-instantiating every plugin
independently. `anime doctor`'s "Plugin manager" check
(`services.doctor_service._check_plugin_manager`) exercises this same
singleton, so running `doctor` before `plugins` in one process (not
possible today since the CLI is one-shot per process, but relevant the
moment anything long-running is built) would see the already-populated
registry rather than re-discovering.

Tests get their own fresh manager per test via an autouse fixture
(`tests/conftest.py::_reset_plugin_manager_singleton`) — process-wide
mutable state needs an explicit reset hook to stay test-isolated, which
is exactly what `services.plugin_service.reset_plugin_manager()` is for.

## Events

**Implemented and wired**, not just declared. `core/events/` is a
strongly-typed async pub/sub bus: `EventBus.subscribe(SomeEvent, handler)`
/ `EventBus.publish(SomeEvent(...))`, keyed by the event's *class*, not a
string name — full autocomplete and type-checking on event fields, no
untyped dict payloads. Defined today, in `core/events/`:

- `plugin_events.py` — `ProviderLoadedEvent`, `ProviderRejectedEvent`,
  `ProviderHealthChangedEvent`. **Actually published** by
  `core.plugin_manager.PluginManager._register()` and
  `.health_check_all()` — not just declared and unused. Covered by
  `tests/unit/test_plugin_manager.py::test_register_publishes_*` and
  `::test_health_check_all_publishes_health_changed_event`.
- `download_events.py` — `DownloadStartedEvent`, `DownloadProgressEvent`,
  `DownloadCompletedEvent`, `DownloadFailedEvent`. Shapes declared now
  (they just wrap the already-existing `models.download.DownloadTask`),
  **no publisher yet** — that's `download/` in Phase 5, consumed by a
  Rich `Live` progress view in `ui/`.
- `metadata_events.py` — `MetadataResolvedEvent`. Same deal: shape
  declared now around the existing `models.media.MediaItem`, publisher
  lands with real metadata plugins in Phase 4.

`PluginManager` takes an `event_bus: EventBus | None` constructor param
(defaulting to `core.events.default_bus`) specifically so tests can
inject a private bus instead of polluting the process-wide one — see
`tests/unit/test_plugin_manager.py::make_manager`.

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

## UI framework (Phase 3)

`ui/` is a full reusable component library — commands never construct a
`rich.table.Table`/`Panel`/etc. directly, they call one of these:

```
ui/
├── capabilities.py    Terminal detection: width/height, color, unicode,
│                      TTY, CI. A process-wide singleton, same pattern as
│                      PluginManager — get_capabilities()/set_capabilities()
│                      (tests)/reset_capabilities().
├── runtime.py          The *resolved* UI state (ascii_mode, animations_
│                      enabled, theme_name, debug) every renderer reads —
│                      decided once in theme.configure_ui(), not re-derived
│                      per component. Third named singleton (see
│                      "Global state is minimal" in
│                      docs/Development-Principles.md).
├── console.py          The single Console object every renderer prints
│                      through. Stable object identity for the process —
│                      configure_ui() mutates it in place (push_theme,
│                      .no_color) rather than replacing it, since replacing
│                      wouldn't be visible through call sites that already
│                      did `from animax.ui.console import console`.
├── theme.py            Palettes (dark/light/ansi) + configure_ui(), which
│                      combines config + capabilities + explicit flags
│                      into the final theme/ascii/animations decision.
├── renderers/
│   ├── icons.py         Status glyphs, ASCII fallback per ui.runtime.
│   ├── styles.py         Named constants for the theme's style keys.
│   └── animations.py     Spinner helper, off in CI/non-TTY/--no-animation.
├── status.py            ✓/✗/⚠/ℹ/○ status-line rendering.
├── tables.py            Generic build_table() + one factory per data
│                      shape already modeled (plugins/downloads/library/
│                      history/metadata) — Phase 4/5/6 call these with
│                      real data, no new table code needed then.
├── panels.py            success/warning/error/info/generic panels.
├── progress.py          Determinate + indeterminate progress bars, ready
│                      for Phase 5's download engine.
├── prompts.py            confirm/text/password/select/multiselect/
│                      path_picker — all refuse to hang in a non-
│                      interactive terminal (raise UiError, or use a
│                      given default).
├── menus.py              A titled, numbered Menu/MenuItem framework —
│                      will power the provider manager, config editor,
│                      episode/search-result pickers (Phase 4/5/6).
├── help.py               The `--help` epilog (env vars, paths, common
│                      workflows) and rich_help_panel category/alias
│                      wiring, used from cli.app.
├── banner.py             Startup wordmark + version + environment
│                      summary — used by `anime about`.
├── config_view.py        The Configuration Viewer: grouped, diffed
│                      current-vs-default tables for `anime config show`.
├── errors.py             The one central error renderer (see
│                      docs/Development-Principles.md "Error presentation").
├── doctor.py / plugins.py   Command-specific renderers built on the
│                      above (tree+summary panel; the plugin table).
├── common.py             success/warning/fatal/tip/note/next_steps/
│                      bullet_list/key_value/horizontal_rule/
│                      section_header/badge/tag — one-liners every
│                      command reaches for instead of ad hoc markup.
└── widgets/tree.py       The grouped status-tree widget doctor uses;
                       the same shape fits the Phase 4/5 per-category
                       provider-health breakdown (docs/Installer.md).
```

**Theming**: four names — `dark` (default palette), `light`, `ansi`
(16-color-safe), `auto` (resolves to `dark` or `ansi` based on detected
color support). Configured via `Settings.theme` and `Settings.ui.accent_color`;
`--no-color`/`--ascii`/`--no-animation` are explicit CLI overrides that
always win over config. See `docs/Configuration.md`.

**Testing pattern**: every ui/ module does `from animax.ui.console import
console`, which binds its own reference — patching
`animax.ui.console.console` in a test wouldn't be visible through an
already-taken binding. `tests/unit/ui/conftest.py`'s `capture_console`
fixture patches the *consuming* module's `console` name instead (a list
of modules when a renderer delegates to another, e.g. `errors.py` calling
`panels.error_panel`).

## Deferred designs

Two structural changes were proposed during Phase 1 review and are
deliberately **not** implemented yet — reshaping `core/interfaces` with
zero real plugins to validate the shape against would likely mean doing
it twice. Written down here so the direction isn't lost.

### `ProviderRegistry` as a layer separate from `PluginManager`

Proposed shape:

```
Application → PluginManager → ProviderRegistry → Provider Instances
```

Today `PluginManager._registry` *is* that registry, just not split out —
there's one flat `dict[str, PluginRecord]` holding every plugin
regardless of category. A dedicated `ProviderRegistry` only earns its
keep once "Plugin" and "Provider" are actually different concepts (next
section): at that point `ProviderRegistry` would hold specifically the
content-supplying categories (metadata/search/download/streaming) that
`PluginManager` discovers and delegates to, while non-provider plugins
(player, notification, auth, and whatever a future generic `Plugin`
mechanism adds) stay directly in `PluginManager`. Build this alongside
the Plugin/Provider split, not before it.

### Typed `ProviderCapabilities` instead of category string matching

Proposed shape: providers advertise structured capabilities —

```python
ProviderCapabilities(
    search=True, metadata=True, episodes=True, stream=False, download=True, magnet=True
)
```

— so core code asks "find providers supporting `SEARCH`" instead of
`if provider.category == "metadata"`. The hook for this already exists
and costs nothing today: `PluginInfo.capabilities: frozenset[str]`
(`models/plugin.py`). It's just untyped strings right now, and nothing
queries it. Rather than guess the flag list (`search`, `metadata`,
`episodes`, `stream`, `download`, `magnet`, ...) before any real
metadata/download plugin exists to confirm it's the right set, Phase 4's
first few concrete plugins should drive what the typed dataclass actually
needs. Turning `capabilities` into a query (`plugin_manager.with_capability("stream")`)
is a small, low-risk addition once that list is real.

### Plugin vs. Provider separation, and Hook Points

Currently every plugin category (`metadata`, `search`, `download`,
`streaming`, `player`, `notification`, `authentication`) is a
`BasePlugin` subclass, registered the same way. The proposed direction —
closer to how VS Code extensions work — is:

- **Provider**: specifically a content-supplying plugin (metadata,
  search, download, streaming) — what `ProviderLoadedEvent` /
  `ProviderRejectedEvent` are already named for, ahead of the split.
- **Plugin**: the generic extension mechanism. One plugin package could
  register *several* contributions at once — providers, CLI commands,
  themes, hooks, services — rather than being locked to exactly one
  `BasePlugin` category. This is what eventually enables plugin types
  the current 7 categories don't cover: Discord/webhook notifications
  (already covered), a theme plugin, a subtitle plugin, an image-cache
  backend, an OCR/translation/AI-metadata-enhancer plugin, etc., without
  each needing its own bespoke core interface.
- **Hook points** (`before_search`, `after_search`, `before_download`,
  `after_download`, `before_play`, `after_play`, `cache_hit`,
  `cache_miss`, alongside the already-implemented `provider_loaded` /
  `provider_health_changed`) are the natural extension of the typed event
  system already built — each hook point is just another `Event`
  subclass, and a generic `Plugin` gets a way to subscribe to
  `core.events` (the missing piece noted in "Public API vs. internal
  implementation" above). No new mechanism needed beyond what
  `core/events/` already provides — just event classes for lifecycle
  points that don't exist yet (`search`, `download`, `play`, `cache`
  aren't real subsystems until Phase 4/5/6) and a way for a `Plugin` to
  register a handler.

This is intentionally a Phase 4 decision, made once `search`/`download`
are being built for real and can validate the split, not a Phase 1
guess.

## Status

Phases 1–3 complete. `core/`, `models/`, `config/`, `database/`, `cache/`,
`installer/`, the singleton plugin manager with typed/wired lifecycle
events, the full `ui/` component library, and the CLI skeleton are
implemented. `download/`, `library/`, `player/`, and all concrete plugins
are placeholders pending Phase 4/5/6 — `ui/`'s data-shaped renderers
(`tables.downloads_table`, `library_table`, `history_table`,
`metadata_table`) already exist and just need real data passed in, per
Phase 3's stated definition of done. `ProviderRegistry`, typed
capabilities, the Plugin/Provider split, and hook points are deliberately
deferred to Phase 4 — see "Deferred designs" above.

# Development Principles

The rules every change to Animax-Cli should hold to, regardless of which
phase or subsystem it touches. Where a rule is already enforced or
verified in code, this document says so and points at it; where it's a
standing intention with nothing to point at yet, it says that too. See
[Architecture.md](Architecture.md) for the reasoning and diagrams behind
most of these — this document is the condensed, imperative form.

## Never import plugins directly

Nothing outside `src/animax/plugins/**` imports a concrete plugin class.
`core/` and `services/` reach plugins only through
`core.plugin_manager.PluginManager`, which hands back instances typed as
`core.interfaces.base.BasePlugin` (or a category ABC) — never a specific
plugin class name. Verified by the import-graph check in
[Architecture.md](Architecture.md#import-graph--verified-no-runtime-cycles)
and by the dependency-direction table there.

## Never block the event loop

All provider-facing plugin methods are `async def`; implementations use
`httpx.AsyncClient`, never a synchronous HTTP call, and never
`time.sleep`. A blocking call inside one plugin's coroutine stalls every
other concurrently-running plugin call sharing that event loop, not just
its own. See [Architecture.md](Architecture.md#async-policy) for the full
policy (including where sync I/O *is* fine — local config/cache reads)
and [Provider-API.md](Provider-API.md#rules).

## No provider-specific logic outside plugins

A plugin translates its provider's native response (JSON, HTML, whatever)
into `animax.models.*` types before returning. Nothing above the plugin
boundary — not `core.plugin_manager`, not `services/`, not `cli/` — ever
sees or parses a provider-native shape. If you find yourself writing
`if provider_name == "anilist":` anywhere outside `plugins/anilist.py`,
that logic belongs inside the plugin, not beside it.

## Services orchestrate; plugins execute

A service decides **what** should happen: which plugins to call, how to
merge/rank/retry their results, what counts as a cache hit. A plugin does
the mechanical work once told: one HTTP request, one file write, one
player launch. See
[Architecture.md](Architecture.md#service-responsibilities) for the
per-service breakdown and the rule of thumb for where new logic belongs.

## Models stay immutable — with named exceptions for state records

Value objects — data that represents a fact, not evolving state — are
frozen (`model_config = ConfigDict(frozen=True)`): `MediaItem`, `Episode`,
`SearchResult`, `ContentSource`, `HistoryEntry`, `PluginInfo`. A service
that needs a different value constructs a new instance; it never mutates
one in place (this is what makes
[normalization ownership](Architecture.md#normalization-ownership)
well-defined — merging never has to reason about who else might be
holding a reference to the object being changed).

Three models are deliberately **not** frozen, because they track state
that evolves over an object's lifetime, and each has exactly one owner
authorized to mutate it:

| Model | Mutated by | Owner |
|---|---|---|
| `PluginRecord` | `core.plugin_manager.PluginManager` (`enabled`, `health`, `shadowed_by`) | `core/` |
| `DownloadTask` | the download engine (`download/`, Phase 5) | `services/` (`download_service`) |
| `LibraryEntry` | `library_service` (Phase 6) | `services/` |

If you're adding a new mutable model, it needs a named owner in this
table — an unowned mutable model is exactly how service boundaries drift.

Caveat: pydantic's `frozen=True` blocks attribute *reassignment*
(`item.title = "x"` raises), not deep immutability of container fields —
`MediaItem.external_ids: dict[str, str]` is technically still mutable in
place. List-valued fields (`alt_titles`, `source_plugins`) are typed
`tuple[str, ...]` specifically to close that gap; `external_ids` stays a
plain `dict` since pydantic has no clean immutable-mapping equivalent.
Treat it as immutable by convention, same as everything else on a frozen
model.

## Core never depends upward

`core/` depends on `models/` only — never on `services/`, `cli/`, or
`plugins/`. See
[Architecture.md](Architecture.md#dependency-direction) for the full
direction table. This is what makes "the core application knows nothing
about individual content providers" (the project's founding principle)
actually true rather than aspirational.

## UI never contains business logic

`ui/*.py` functions take already-computed data (a `list[CheckResult]`, a
`list[PluginRecord]`) and render it with Rich — they never call a
service, never make a decision about *what* to display beyond formatting.
`cli/commands/*.py` is the thin controller that calls a service, then
hands the result to `ui/`; if a `ui/` function needs to call `services/`
to get more information, that's a sign the decision belongs in the
command or the service, not in `ui/`.

As of Phase 3's full `ui/` component library (docs/Architecture.md "UI
framework"), the flip side of this rule is now concrete too: **`cli/`
never constructs a Rich object directly** — every table/panel/prompt/
status line goes through `ui/`, never a bare `rich.table.Table(...)` or
`console.print(f"[green]...")` inline in a command file. `ui/tables.py`'s
sort-order parameter is the one deliberate exception — see its docstring
for why presentation *order* is allowed there while data *selection*
still isn't.

## Global state is minimal, and every instance is named here

Prefer passing dependencies explicitly (a constructor argument, a
function parameter) over reaching for a global. When a process-wide
singleton is genuinely the right shape — one shared thing, one process,
no meaningful "which instance" question — it's allowed, but it must be
named in this list, with a reset hook for tests. Today, that's exactly
four:

| Singleton | Module | Reset hook (tests) |
|---|---|---|
| `PluginManager` | `services.plugin_service` | `reset_plugin_manager()` |
| Default `EventBus` | `core.events.default_bus` | inject a private `EventBus()` instead of using it |
| Resolved UI state (ascii/animations/theme/debug) | `ui.runtime` | `reset()` |
| Terminal capabilities snapshot | `ui.capabilities` | `reset_capabilities()` |

An unnamed fifth singleton is a bug, not a convenience — `tests/conftest.py`
resets all four via autouse fixtures specifically because process-wide
mutable state that isn't reset between tests causes exactly the kind of
flaky, order-dependent test failures this list exists to prevent.

## One responsibility per module

A file under `services/` owns one thing (search orchestration, plugin
discovery, doctor checks — see
[Architecture.md](Architecture.md#service-responsibilities)), not several
unrelated ones bundled because they happened to be convenient to write
together. The same discipline applies inside `core/`: `plugin_manager.py`
only discovers/validates/tracks plugins, `versioning.py` only does SemVer
parsing/comparison, `events/` only does pub/sub — none of them reach into
what the others own.

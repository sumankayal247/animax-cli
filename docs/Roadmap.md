# Roadmap

## Phase 1 — Bootstrap

Project planning, architecture, folder structure, dependency selection,
CLI skeleton, configuration system, project bootstrap, documentation.
**Status: implemented.**

## Phase 2 — Core framework

Plugin manager (implemented in Phase 1, ahead of schedule since it's the
project's highest priority — now a process-wide singleton with idempotent
discovery, see docs/Architecture.md "Plugin Manager: singleton, not
per-call"), abstract interfaces (implemented), typed event bus
(implemented and wired into plugin lifecycle — see docs/Architecture.md
"Events"), file-based/structured logging and crash reports (console
logging only so far), caching (basic TTL store implemented; cleanup
scheduling still open), SQLite (schema + connection implemented; query
helpers pending), richer error handling.

Config schema version compatibility-checking/migration logic (the field
already exists, nothing compares it yet — see docs/Architecture.md
"Versioning") also belongs here, whenever `CONFIG_SCHEMA_VERSION` is
first bumped. **Status: implemented.**

## Phase 3 — Rich terminal UI

A full reusable component library under `ui/` — theme (dark/light/ansi/auto),
terminal capability detection, tables, panels, status indicators, progress
bars (single/multi/spinner/transfer/ETA), interactive prompts (confirm/
select/multiselect/text/password/path-picker), a menu framework, a
polished `--help` (env vars, paths, command categories, an alias),
a central error renderer with crash-report persistence, a Configuration
Viewer, an upgraded doctor UI (tree + summary + recommendations), and
accessibility fallbacks (`--ascii`, `--no-color`, `--no-animation`,
auto-disabled animations in CI/non-TTY). See docs/Architecture.md
"UI framework (Phase 3)" for the full component map.

No provider/download/streaming logic was added, per the phase's own
rule — `tables.py`'s `downloads_table`/`library_table`/`history_table`/
`metadata_table` render the models that already exist
(`DownloadTask`/`LibraryEntry`/`HistoryEntry`/`MediaItem`) but have no
real data source yet; Phase 4/5/6 call them, not rebuild them.
**Status: implemented.**

## Phase 4 — Metadata plugin framework

Split into two sub-phases: 4B's structural redesign depends on having a
few real plugins in hand to validate the shape against, so it comes
*after* 4A produces them — not in parallel.

### Phase 4: Metadata & Discovery Engine
- [x] Expand `MediaItem` and `Episode` domain models (Season, Studio, Genres).
- [x] Implement robust Search Pipeline (`animax.services.search_service`).
- [x] Implement Metadata Aggregation Pipeline (`animax.services.metadata_service`).
- [x] Implement AniList metadata provider.
- [x] CLI integration (`anime search`, `anime info`, `anime episodes`).

### Phase 4 Extras: Intelligent Search & Discovery
- [x] Media Type Support (`MediaType` enum, plugin mapping).
- [x] Intelligent Search & Fuzzy Matching (`difflib`, partial matching, string normalization).
- [x] Ranking Engine (scores based on exact, partial, fuzzy matches, and completeness).
- [x] Interactive Selection & CLI Flags (`--first`, `--limit`, `--exact`, `--json`).
- [x] Metadata Events (`SearchNormalized`, `SearchRanked`, `SuggestionsGenerated`, `SearchAmbiguous`).

### Phase 4B — Provider redesign

The structural decisions deferred after Phase 1 review, made once 4A's
plugins exist to validate them against — see docs/Architecture.md
"Deferred designs" for the reasoning on each:

- Split `ProviderRegistry` out from `PluginManager` (only makes sense
  alongside the Plugin/Provider split below).
- Turn `PluginInfo.capabilities` from untyped strings into a typed,
  queryable `ProviderCapabilities`.
- Separate generic `Plugin` (one package registering providers, commands,
  themes, hooks, services) from `Provider` (specifically
  metadata/search/download/streaming).
- Hook points (`before_search`, `after_search`, `provider_loaded`,
  `cache_hit`, etc.) as more `core.events` event classes, plus a way for
  a generic `Plugin` to subscribe to them.
- Wire `BasePlugin.setup()`/`.teardown()`, and the concurrency/timeout/
  retry policy from docs/Plugin-System.md, into how 4A's plugins actually
  get called — 4A can ship without these (sequential calls, no explicit
  timeout) and 4B tightens it once the redesign lands.

## Phase 5 — Download framework

Queue, resume, retry, verification, parallel downloads (`download/`),
media player integration (`player/`), wiring `anime download` / `play`.

## Phase 6 — Library, history, cache/config polish

`library/`, `anime library` / `history` / `cache` / `logs` /
`config set`.

## Phase 7 — Installer, doctor, packaging

`anime doctor` already has an overall "Plugin manager" row (Phase 1); the
per-category breakdown (a "Metadata Providers" / "Download Providers"
tree with one row per provider, a "Media Players" row) lands alongside
the plugins/players that make it meaningful — Phase 4/5, not here.
Remaining Phase 7 doctor work: network connectivity, disk space, and the
first-run experience (OS detection, welcome screen, platform-specific
install guidance), cross-platform verification, packaging, `anime update`
/ `diagnose`, release preparation.

## Phase 8 — Performance, cleanup, release candidate

Optimization, refactoring, documentation audit, test audit.

See [Future-Ideas.md](Future-Ideas.md) for ideas beyond Phase 8.

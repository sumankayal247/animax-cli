# Roadmap

## Phase 1 — Bootstrap (current)

Project planning, architecture, folder structure, dependency selection,
CLI skeleton, configuration system, project bootstrap, documentation.
**Status: implemented**, pending review.

## Phase 2 — Core framework

Plugin manager (implemented in Phase 1, ahead of schedule since it's the
project's highest priority), abstract interfaces (implemented), event bus
(implemented), file-based/structured logging and crash reports (console
logging only so far), caching (basic TTL store implemented; cleanup
scheduling still open), SQLite (schema + connection implemented; query
helpers pending), richer error handling.

## Phase 3 — Rich terminal UI

Tables, panels, progress bars, live updates, interactive prompts, themes,
help system polish beyond the current baseline theme.

## Phase 4 — Metadata plugin framework

Plugin registration is generic and already works (Phase 1); this phase is
about *implementing real metadata plugins* (AniList, MAL, Kitsu, TMDB,
TVMaze, OMDb as appropriate), plugin configuration, search aggregation
(merge/normalize/rank), and wiring `anime search` / `info` / `episodes`.

## Phase 5 — Download framework

Queue, resume, retry, verification, parallel downloads (`download/`),
media player integration (`player/`), wiring `anime download` / `play`.

## Phase 6 — Library, history, cache/config polish

`library/`, `anime library` / `history` / `cache` / `logs` /
`config set`.

## Phase 7 — Installer, doctor, packaging

Remaining doctor checks (player, plugin health, network, disk), first-run
experience, cross-platform verification, packaging, `anime update` /
`diagnose`, release preparation.

## Phase 8 — Performance, cleanup, release candidate

Optimization, refactoring, documentation audit, test audit.

See [Future-Ideas.md](Future-Ideas.md) for ideas beyond Phase 8.

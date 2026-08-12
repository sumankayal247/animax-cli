# CLI Commands

Installed as `anime` (see `[project.scripts]` in `pyproject.toml`).

| Command           | Status         | Notes |
|--------------------|---------------------------|-------|
| `anime search QUERY` | Implemented | metadata + search plugin aggregation |
| `anime info ID`      | Implemented | |
| `anime episodes ID`  | Implemented | |
| `anime download ID`  | placeholder → Phase 5  | |
| `anime play ID`      | placeholder → Phase 5  | |
| `anime library`      | placeholder → Phase 6  | |
| `anime history`      | placeholder → Phase 6  | |
| `anime config show`  | **implemented**            | formatted Configuration Viewer (grouped, current-vs-default); `--json` for raw JSON |
| `anime config path`  | **implemented**            | prints the config file path |
| `anime config set K V` | placeholder → Phase 6 | |
| `anime plugins` (alias `ls`) | **implemented**    | discovers and lists all plugins with source/priority/capabilities/health |
| `anime doctor`       | **implemented**            | see [Installer.md](Installer.md); tree + summary + recommendations; `--verbose`/`--json` output modes planned, Phase 7 |
| `anime logs`         | placeholder → Phase 6  | |
| `anime cache`        | placeholder → Phase 6  | |
| `anime update`       | placeholder → Phase 7  | |
| `anime version`      | **implemented**            | |
| `anime about`        | **implemented**            | startup banner + environment summary (`ui.banner` config-gated) |
| `anime diagnose`     | placeholder → Phase 7  | |

## Global flags (root callback, `cli/app.py`)

| Flag | Effect |
|---|---|
| `--debug` | DEBUG-level logging, Rich tracebacks on errors, full traceback on unexpected errors |
| `--verbose` / `-v` | INFO-level console logging |
| `--ascii` | Force plain ASCII output (icons, box-drawing) regardless of detected unicode support |
| `--no-color` | Disable colored output (also honors the `NO_COLOR` env var automatically) |
| `--no-animation` | Disable spinners/live-updating output |

Animations are also automatically disabled in CI or when output isn't a
real TTY, independent of `--no-animation` — see docs/Architecture.md "UI
framework (Phase 3)".

## Command categories and structure

Commands are grouped in `--help` output via Typer's `rich_help_panel`
(`ui.help.CATEGORY_CONTENT`/`CATEGORY_SYSTEM`/`CATEGORY_INFO`) — Content
(search/info/episodes/download/play/library/history), System
(config/plugins/doctor/logs/cache/update), Info (version/about/diagnose).

Every command module under `cli/commands/` follows the same shape: a
`register(app: typer.Typer) -> None` function that adds one (or, for
`config`, a `typer.Typer` sub-app of several) commands. Commands stay thin
— argument parsing and rendering via `ui/` only; all logic is in
`services/`. Async commands use the shared `cli.commands._common.run_async`
decorator instead of hand-rolling `asyncio.run(...)`.

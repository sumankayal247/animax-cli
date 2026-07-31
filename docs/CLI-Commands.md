# CLI Commands

Installed as `anime` (see `[project.scripts]` in `pyproject.toml`).

| Command           | Status (Phase 1)         | Notes |
|--------------------|---------------------------|-------|
| `anime search QUERY` | placeholder → Phase 4  | metadata + search plugin aggregation |
| `anime info ID`      | placeholder → Phase 4  | |
| `anime episodes ID`  | placeholder → Phase 4  | |
| `anime download ID`  | placeholder → Phase 5  | |
| `anime play ID`      | placeholder → Phase 5  | |
| `anime library`      | placeholder → Phase 6  | |
| `anime history`      | placeholder → Phase 6  | |
| `anime config show`  | **implemented**            | prints resolved settings as JSON |
| `anime config path`  | **implemented**            | prints the config file path |
| `anime config set K V` | placeholder → Phase 6 | |
| `anime plugins`      | **implemented**            | discovers and lists all plugins with source/priority/health |
| `anime doctor`       | **implemented**            | see [Installer.md](Installer.md) |
| `anime logs`         | placeholder → Phase 6  | |
| `anime cache`        | placeholder → Phase 6  | |
| `anime update`       | placeholder → Phase 7  | |
| `anime version`      | **implemented**            | |
| `anime about`        | **implemented**            | |
| `anime diagnose`     | placeholder → Phase 7  | |

`--debug` is a global flag (root callback in `cli/app.py`) that raises
console log verbosity and enables Rich tracebacks.

Every command module under `cli/commands/` follows the same shape: a
`register(app: typer.Typer) -> None` function that adds one (or, for
`config`, a `typer.Typer` sub-app of several) commands. Commands stay thin
— argument parsing and Rich rendering only; all logic is in `services/`.

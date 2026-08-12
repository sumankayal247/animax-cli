# Developer Guide

## Running locally

```bash
uv sync
uv run anime --help
uv run anime doctor
uv run anime plugins
uv run anime config path
uv run anime config show
```

## Project layout

See [Architecture.md](Architecture.md) for the full picture. In short:
`cli/` is thin controllers, `services/` is business logic, `core/` is the
plugin framework, `models/` is shared data shapes, everything else
(`config/`, `database/`, `cache/`, `download/`, `library/`, `player/`,
`installer/`, `ui/`) is a focused subsystem `services/` orchestrates.

Before writing non-trivial code, read
[Development-Principles.md](Development-Principles.md) — it's the short,
imperative rule set (services orchestrate/plugins execute, models stay
immutable, core never depends upward, etc.) that keeps the layers above
from drifting into each other.

## Adding a new CLI command

1. Create `src/animax/cli/commands/<name>.py` with a
   `register(app: typer.Typer) -> None` function.
2. Add the module to the import list and `_COMMAND_MODULES` tuple in
   `src/animax/cli/app.py`.
3. Put any real logic in a new or existing `services/*.py` — the command
   function itself should just parse args, call the service, and render
   with `ui/`.
4. Update [CLI-Commands.md](CLI-Commands.md).

## Adding a new plugin

See `src/animax/plugins/unknown_providers.txt` and
[Plugin-System.md](Plugin-System.md).

## Adding a config option

1. Add the field to the relevant model in `src/animax/config/schema.py`.
2. Update the example in [Configuration.md](Configuration.md).
3. If the change isn't backward compatible, bump `CONFIG_SCHEMA_VERSION`
   in `core/constants.py` and add a migration step to
   `config/loader.py`.

## Type checking, linting, formatting

```bash
uv run mypy src
uv run ruff check .
uv run black .
```

## Tests

```bash
uv run pytest
```

# Contributing

## Setup

```bash
git clone <repo-url>
cd animax-cli
uv sync
uv run anime doctor
uv run pytest
```

## Before opening a PR

```bash
uv run ruff check .
uv run black --check .
uv run mypy src
uv run pytest
```

## Conventions

- Python 3.12+, full type hints, `mypy --strict` must pass.
- Read [Development-Principles.md](Development-Principles.md) —
  it's the condensed rule set (never import plugins directly, services
  orchestrate/plugins execute, models stay immutable, etc.) that the
  points below are specific instances of.
- Commands (`cli/commands/*.py`) stay thin controllers — no business logic;
  put it in `services/`.
- Never import `animax.plugins.*` from `core/` or `services/` — talk to
  `core.plugin_manager.PluginManager` instead.
- New plugin? Read `src/animax/plugins/unknown_providers.txt` and
  [Plugin-System.md](Plugin-System.md) first.
- Small commits, one logical change each, meaningful messages.
- Update the relevant `docs/*.md` in the same PR as the code it documents
  — don't let docs drift behind implementation.

## Tests

- Unit tests: `tests/unit/`, mirroring the `src/animax/` package layout.
- Integration tests: `tests/integration/`.
- No live network calls in tests — mock `httpx` responses.

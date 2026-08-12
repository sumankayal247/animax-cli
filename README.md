# Animax-Cli

A modern, plugin-based terminal media CLI framework — beautiful, fast, cross-platform, and built to be extended.

Animax-Cli is **not** a clone of any existing anime/media CLI. It's a general framework: the core application knows nothing about individual content providers. Everything — metadata sources, download backends, streaming resolvers, local players — is a plugin discovered and orchestrated through a common Plugin Manager. One broken plugin never crashes the app.

## Status

Early development (Phases 1–3 — bootstrap, core framework, terminal UI).
Core infrastructure and a polished, reusable terminal UI are in place;
no content providers exist yet, so search/download/play aren't
functional for end users (see [docs/Roadmap.md](docs/Roadmap.md)).

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency and environment management

## Development setup

```bash
uv sync
uv run anime --help
uv run anime doctor
uv run anime plugins
uv run anime config show
uv run anime about
```

`--debug`, `--verbose`/`-v`, `--ascii`, `--no-color`, and `--no-animation`
are global flags — see [docs/CLI-Commands.md](docs/CLI-Commands.md).

## Project layout

See [docs/Architecture.md](docs/Architecture.md) for the full architecture, [docs/Development-Principles.md](docs/Development-Principles.md) for the rules every change should hold to, and [docs/Developer-Guide.md](docs/Developer-Guide.md) for contributor setup.

## Plugins

Animax-Cli plugins can be:

- **Built-in** — bundled under `src/animax/plugins/`
- **User-installed** — dropped into your user plugin directory (see `anime doctor` / `anime config` for the path), no packaging required
- **PyPI-distributed** — installed as separate packages that register via the `animax.plugins` entry-point group

See [docs/Plugin-System.md](docs/Plugin-System.md) and [docs/Provider-API.md](docs/Provider-API.md) to build your own, and `src/animax/plugins/unknown_providers.txt` for the developer backlog of provider ideas (never read by the app itself).

## License

Apache License 2.0 — see [LICENSE](LICENSE).

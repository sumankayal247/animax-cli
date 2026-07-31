# Player System

**Status: not yet implemented — planned for Phase 5.**

## Scope

`player/` will detect installed local players in preferred order:

1. MPV
2. VLC
3. System default

Each is a `PlayerPlugin` (`core/interfaces/player.py`) with
`is_available()` (binary/app detected on `PATH` or known install
locations per OS) and `async play(target, *, resume_at_seconds=None)`.

If none are found, `anime doctor` / first-run setup shows platform-specific
installation guidance (Windows, Debian/Ubuntu, Fedora, Arch, macOS) —
Animax-Cli never attempts to install a player automatically.

Player choice is configurable via `player.preferred_order` in
`settings.toml` (see [Configuration.md](Configuration.md)).

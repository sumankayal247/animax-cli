# Installer / Doctor

`anime doctor` (`services/doctor_service.py`, checks in `installer/checks.py`)
runs a set of `CheckResult`s and renders them as a Rich table
(`ui/doctor.py`). Exit code is `0` if every check passed, `1` otherwise —
suitable for CI or scripting.

## Phase 1 checks

- Python version ≥ 3.12
- Config directory exists and is writable
- Cache directory exists and is writable
- Data directory exists and is writable
- Log directory exists and is writable
- Database initializes successfully

## Planned (later phases)

- Media player availability (Phase 5, once `player/` exists)
- Plugin health (Phase 4, once `core.plugin_manager.health_check_all()`
  is wired into the doctor flow)
- Network connectivity
- Disk space
- Required Python package versions (beyond what `uv sync` already
  guarantees)
- First-run experience: OS detection, welcome screen, platform-specific
  install guidance for missing optional dependencies (Windows,
  Debian/Ubuntu, Fedora, Arch, macOS) — see [Roadmap.md](Roadmap.md) Phase 7.

`anime doctor` itself is fully implemented for the Phase 1 checks above.
`anime diagnose` will extend it with the remaining checks once those
subsystems exist (player, plugin health, network, disk) — until then it's
a placeholder.

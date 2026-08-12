# Installer / Doctor

`anime doctor` (`services/doctor_service.py`, checks in `installer/checks.py`)
runs a set of `CheckResult`s and renders them as a grouped status tree
with a pass/fail summary panel and, on failure, a recommendations panel
(`ui/doctor.py`, built on `ui.widgets.tree` — see docs/Architecture.md
"UI framework (Phase 3)"). Exit code is `0` if every check passed, `1`
otherwise — suitable for CI or scripting.

## Phase 1 checks

- Python version ≥ 3.12
- Config directory exists and is writable
- Cache directory exists and is writable
- Data directory exists and is writable
- Log directory exists and is writable
- Database initializes successfully
- Plugin manager: discovery runs via the singleton `PluginManager`
  (`services.plugin_service.get_plugin_manager()`) without raising. This
  passes even if individual plugins are rejected — rejections are
  expected, isolated failures (see docs/Plugin-System.md), surfaced as a
  warning count pointing to `anime plugins` for detail, not a doctor
  failure. Only an exception escaping discovery itself fails this check.

## Planned (later phases)

- Per-provider health, broken into category rows ("Metadata Providers",
  "Download Providers", one line per provider) using
  `core.plugin_manager.PluginManager.health_check_all()` — meaningful
  once Phase 4/5 plugins exist to check; the manager-level check above
  already exists today.
- Media player availability (Phase 5, once `player/` exists)
- Network connectivity
- Disk space
- Required Python package versions (beyond what `uv sync` already
  guarantees)
- First-run experience: OS detection, welcome screen, platform-specific
  install guidance for missing optional dependencies (Windows,
  Debian/Ubuntu, Fedora, Arch, macOS) — see [Roadmap.md](Roadmap.md) Phase 7.

### External dependency detection (planned, Phase 7)

Beyond Python packages (`uv sync` already guarantees those), `anime
doctor` should detect the external binaries the project depends on as
each subsystem starts needing them, reporting found/missing + version
where relevant rather than failing silently later when a feature tries
to shell out to one:

| Dependency | Needed by | Detection |
|---|---|---|
| `mpv` | `player/` (Phase 5) | on `PATH` / known per-OS install locations |
| `vlc` | `player/` (Phase 5) | on `PATH` / known per-OS install locations |
| `ffmpeg` | `download/` verification, possible transcoding (Phase 5) | on `PATH` |
| `aria2c` | possible parallel-download backend (Phase 5, if adopted) | on `PATH` |
| `git` | contributor workflow, not an end-user runtime dependency | on `PATH` |
| `python` | already checked (Phase 1: `check_python_version`) | `sys.version_info` |

A missing optional dependency is a warning with install guidance (per
platform — see "First-run experience" above), never a hard failure;
`anime doctor`'s existing exit-code contract (0 = all checks passed) only
changes if a *required* dependency for an *enabled* feature is missing.

### Doctor verbosity (planned, Phase 7)

```
anime doctor            # current: status tree + summary/recommendations panels
anime doctor --verbose  # planned: include detail/fix text inline for
                         # passing checks too, not just failing ones
anime doctor --json     # planned: machine-readable CheckResult list —
                         # useful for CI gating and for users attaching
                         # doctor output to a bug report
```

`--json` serializes the same `list[CheckResult]`
`services.doctor_service.run_checks()` already returns today — no new
check logic needed, just an alternate `ui/` renderer
(`ui.doctor.render_doctor_results` gets a JSON-output sibling) selected
by the flag, following the same thin-controller pattern as every other
command.

`anime doctor` itself is fully implemented for the Phase 1 checks above.
`anime diagnose` will extend it with the remaining checks once those
subsystems exist (per-provider health, player, network, disk) — until
then it's a placeholder.

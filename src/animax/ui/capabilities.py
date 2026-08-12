"""Terminal capability detection: width/height, color, unicode, TTY, CI.

Detected once per process and cached (same singleton-with-override shape
as core.plugin_manager's process-wide manager — see
docs/Development-Principles.md "Global state is minimal, and every
instance is named here" for why this is an intentionally documented
global, not an accidental one). `cli.app`'s root
callback resolves this before any command renders; tests call
`set_capabilities()` to inject a fixed value instead of probing the real
environment.
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass

from rich.console import Console

#: Environment variables that conventionally indicate a CI runner.
_CI_ENV_VARS = ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "JENKINS_URL")


@dataclass(frozen=True, slots=True)
class TerminalCapabilities:
    """A snapshot of what the current terminal can actually do."""

    width: int
    height: int
    is_tty: bool
    is_ci: bool
    supports_color: bool
    supports_unicode: bool
    platform_name: str

    @property
    def is_interactive(self) -> bool:
        """True if prompts/animations are safe to show (a real TTY, not CI)."""
        return self.is_tty and not self.is_ci

    @property
    def is_narrow(self) -> bool:
        """True if the terminal is too narrow for a full-width table layout."""
        return self.width < 80


def _detect_unicode_support() -> bool:
    encoding = (sys.stdout.encoding or "").lower()
    return "utf" in encoding


def detect(*, probe_console: Console | None = None) -> TerminalCapabilities:
    """Probe the real environment. Call once; prefer get_capabilities() elsewhere."""
    size = shutil.get_terminal_size(fallback=(100, 24))
    probe = probe_console or Console(stderr=True)
    is_ci = any(os.environ.get(var) for var in _CI_ENV_VARS)
    return TerminalCapabilities(
        width=size.columns,
        height=size.lines,
        is_tty=sys.stdout.isatty(),
        is_ci=is_ci,
        supports_color=probe.color_system is not None and "NO_COLOR" not in os.environ,
        supports_unicode=_detect_unicode_support(),
        platform_name=platform.system(),
    )


_capabilities: TerminalCapabilities | None = None


def get_capabilities() -> TerminalCapabilities:
    """Return the process-wide capabilities snapshot, detecting on first use."""
    global _capabilities
    if _capabilities is None:
        _capabilities = detect()
    return _capabilities


def set_capabilities(capabilities: TerminalCapabilities) -> None:
    """Override the cached capabilities — for `cli.app` (explicit flags) and tests."""
    global _capabilities
    _capabilities = capabilities


def reset_capabilities() -> None:
    """Drop the cached snapshot so the next get_capabilities() re-detects."""
    global _capabilities
    _capabilities = None

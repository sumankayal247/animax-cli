"""Semantic Versioning helpers used for the app, plugin API, and config schema.

Animax-Cli tracks three independent SemVer numbers (see core.constants):

- The application version (``animax.__version__``).
- ``PLUGIN_API_VERSION`` — the plugin interface contract.
- ``CONFIG_SCHEMA_VERSION`` — the on-disk config file shape.

This module implements minimal SemVer parsing and the compatibility rule
used across the codebase: two versions are *compatible* if they share the
same MAJOR version. A MAJOR bump signals a breaking change; MINOR/PATCH
bumps must remain backward compatible within a MAJOR line.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?(?:\+(?P<build>[0-9A-Za-z.-]+))?$"
)


@dataclass(frozen=True, order=True, slots=True)
class Version:
    """A parsed Semantic Version (https://semver.org)."""

    major: int
    minor: int
    patch: int
    prerelease: str | None = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.prerelease}" if self.prerelease else base

    @classmethod
    def parse(cls, raw: str) -> Version:
        match = _SEMVER_RE.match(raw.strip())
        if not match:
            raise ValueError(f"{raw!r} is not a valid Semantic Version (MAJOR.MINOR.PATCH)")
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=match.group("prerelease"),
        )

    def is_compatible_with(self, other: Version) -> bool:
        """True if ``other`` can be used where this version is expected.

        Same-MAJOR is compatible per SemVer convention; a differing MAJOR
        is treated as a breaking change.
        """
        return self.major == other.major


def parse(raw: str) -> Version:
    """Convenience wrapper around :meth:`Version.parse`."""
    return Version.parse(raw)


def is_compatible(required: str, actual: str) -> bool:
    """True if the ``actual`` version satisfies the ``required`` version's MAJOR line."""
    return Version.parse(required).is_compatible_with(Version.parse(actual))

"""Base exception types shared across the application.

Every user-facing error should ultimately be (or wrap) an ``AnimaxError``.
The CLI layer catches ``AnimaxError`` at the top level and renders its
``message``/``reason``/``fix`` as a friendly Rich panel instead of a raw
traceback (see cli.commands and ui.errors).
"""

from __future__ import annotations


class AnimaxError(Exception):
    """Base class for all Animax-Cli errors.

    Attributes:
        message: What happened, in plain language.
        reason: Why it happened, if known.
        fix: A suggested next step for the user.
    """

    def __init__(self, message: str, *, reason: str | None = None, fix: str | None = None) -> None:
        self.message = message
        self.reason = reason
        self.fix = fix
        super().__init__(message)


class ConfigError(AnimaxError):
    """Raised for configuration load/save/validation failures."""


class DatabaseError(AnimaxError):
    """Raised for database initialization or query failures."""


class PluginError(AnimaxError):
    """Base class for plugin-related errors."""


class PluginLoadError(PluginError):
    """Raised when a plugin fails to import or instantiate."""


class PluginValidationError(PluginError):
    """Raised when a plugin fails interface/metadata validation."""


class PluginVersionMismatchError(PluginError):
    """Raised when a plugin declares an incompatible PLUGIN_API_VERSION."""


class ServiceError(AnimaxError):
    """Raised for business-logic failures inside services/."""


class UiError(AnimaxError):
    """Raised for UI-specific failures."""

"""The resolved, process-wide UI state every renderer reads from.

Distinct from `capabilities.py` (what the terminal *can* do) — this is
what the UI has *decided* to do, after combining capabilities with config
and explicit CLI flags (`--ascii`, `--no-animation`, `--no-color`). Set
once by `ui.console.configure_ui()` (called from `cli.app`'s root
callback); every renderer (icons, animations, progress, tables) reads it
instead of re-deriving the decision itself, so "should this look ASCII"
has exactly one answer, decided in exactly one place.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class UiRuntimeState:
    ascii_mode: bool = False
    animations_enabled: bool = True
    theme_name: str = "dark"
    debug: bool = False


_state = UiRuntimeState()


def get_state() -> UiRuntimeState:
    return _state


def configure(
    *,
    ascii_mode: bool | None = None,
    animations_enabled: bool | None = None,
    theme_name: str | None = None,
    debug: bool | None = None,
) -> None:
    """Update whichever fields are given; leaves the rest untouched."""
    global _state
    _state = replace(
        _state,
        ascii_mode=_state.ascii_mode if ascii_mode is None else ascii_mode,
        animations_enabled=(
            _state.animations_enabled if animations_enabled is None else animations_enabled
        ),
        theme_name=_state.theme_name if theme_name is None else theme_name,
        debug=_state.debug if debug is None else debug,
    )


def reset() -> None:
    global _state
    _state = UiRuntimeState()

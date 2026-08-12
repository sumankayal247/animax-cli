"""Status/severity icon sets, with an ASCII fallback for every glyph.

Every renderer that needs an icon calls `icon(name)` — never hardcodes a
literal glyph — so ascii_mode (ui.runtime) flips every icon at once.
"""

from __future__ import annotations

from animax.ui.runtime import get_state

_UNICODE_ICONS: dict[str, str] = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "pending": "○",
    "running": "◐",
    "bullet": "•",
    "arrow": "→",
}

_ASCII_ICONS: dict[str, str] = {
    "success": "[OK]",
    "error": "[X]",
    "warning": "[!]",
    "info": "[i]",
    "pending": "[ ]",
    "running": "[~]",
    "bullet": "-",
    "arrow": "->",
}


def icon(name: str) -> str:
    """The glyph for ``name`` (see the keys above), honoring ui.runtime.ascii_mode."""
    icons = _ASCII_ICONS if get_state().ascii_mode else _UNICODE_ICONS
    return icons.get(name, icons["bullet"])

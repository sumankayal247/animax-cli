"""The shared Rich theme and console instance every CLI command renders through."""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

from animax.ui.capabilities import TerminalCapabilities, get_capabilities
from animax.ui.runtime import configure


def resolve_theme_name(configured: str, capabilities: TerminalCapabilities) -> str:
    if configured in ("light", "dark", "ansi"):
        return configured
    if capabilities.supports_color:
        return "dark"
    return "ansi"

def build_rich_theme(theme_name: str, accent: str | None = None) -> Theme:
    styles = {
        "animax.title": "bold magenta",
        "animax.success": "bold green",
        "animax.warning": "bold yellow",
        "animax.error": "bold red",
        "animax.info": "cyan",
        "animax.muted": "dim",
    }
    if accent:
        styles["animax.accent"] = accent
    return Theme(styles)

def provider_color(index: int) -> str:
    colors = ["magenta", "cyan", "green", "yellow", "blue", "red"]
    return colors[index % len(colors)]

ANIMAX_THEME = build_rich_theme("dark")
console = Console(theme=ANIMAX_THEME)

def configure_ui(
    configured_theme: str = "auto",
    animations_enabled: bool = True,
    ascii_mode: bool = False,
    no_color: bool = False,
    accent: str | None = None,
) -> None:
    caps = get_capabilities()
    
    if no_color:
        theme_name = "ansi"
    else:
        theme_name = resolve_theme_name(configured_theme, caps)
        
    final_ascii = ascii_mode if ascii_mode else not caps.supports_unicode
    final_animations = animations_enabled and caps.is_tty and not caps.is_ci
    
    configure(
        theme_name=theme_name,
        ascii_mode=final_ascii,
        animations_enabled=final_animations
    )
    
    global console
    console = Console(theme=build_rich_theme(theme_name, accent=accent))

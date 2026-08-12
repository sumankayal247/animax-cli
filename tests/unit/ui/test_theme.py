from __future__ import annotations

from animax.ui.capabilities import TerminalCapabilities, set_capabilities
from animax.ui.runtime import get_state
from animax.ui.theme import build_rich_theme, configure_ui, provider_color, resolve_theme_name


def _caps(**overrides: object) -> TerminalCapabilities:
    base = dict(
        width=100,
        height=24,
        is_tty=True,
        is_ci=False,
        supports_color=True,
        supports_unicode=True,
        platform_name="Linux",
    )
    base.update(overrides)
    return TerminalCapabilities(**base)  # type: ignore[arg-type]


def test_resolve_theme_name_passthrough() -> None:
    caps = _caps()
    assert resolve_theme_name("light", caps) == "light"
    assert resolve_theme_name("dark", caps) == "dark"
    assert resolve_theme_name("ansi", caps) == "ansi"


def test_resolve_theme_name_auto_prefers_dark_when_color_supported() -> None:
    caps = _caps(supports_color=True)
    assert resolve_theme_name("auto", caps) == "dark"


def test_resolve_theme_name_auto_falls_back_to_ansi_without_color() -> None:
    caps = _caps(supports_color=False)
    assert resolve_theme_name("auto", caps) == "ansi"


def test_resolve_theme_name_unknown_value_behaves_like_auto() -> None:
    caps = _caps(supports_color=True)
    assert resolve_theme_name("default", caps) == "dark"


def test_build_rich_theme_applies_accent_override() -> None:
    theme = build_rich_theme("dark", accent="blue")
    assert theme.styles["animax.accent"].color is not None


def test_provider_color_cycles() -> None:
    colors = [provider_color(i) for i in range(8)]
    assert colors[0] == colors[6]  # wraps after 6 provider colors


def test_configure_ui_sets_runtime_state() -> None:
    set_capabilities(_caps(supports_unicode=False, is_ci=False, is_tty=True))
    configure_ui(configured_theme="dark", animations_enabled=True)
    state = get_state()
    assert state.theme_name == "dark"
    assert state.ascii_mode is True  # auto-detected from supports_unicode=False


def test_configure_ui_explicit_ascii_overrides_detection() -> None:
    set_capabilities(_caps(supports_unicode=True))
    configure_ui(configured_theme="dark", ascii_mode=True)
    assert get_state().ascii_mode is True


def test_configure_ui_no_color_forces_ansi_theme() -> None:
    set_capabilities(_caps(supports_color=True))
    configure_ui(configured_theme="dark", no_color=True)
    assert get_state().theme_name == "ansi"


def test_configure_ui_disables_animations_when_not_interactive() -> None:
    set_capabilities(_caps(is_ci=True))
    configure_ui(configured_theme="dark", animations_enabled=True)
    assert get_state().animations_enabled is False

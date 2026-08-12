from __future__ import annotations

from animax.ui.capabilities import (
    TerminalCapabilities,
    get_capabilities,
    reset_capabilities,
    set_capabilities,
)


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


def test_get_capabilities_detects_on_first_use() -> None:
    reset_capabilities()
    caps = get_capabilities()
    assert isinstance(caps, TerminalCapabilities)
    assert caps.width > 0


def test_set_capabilities_overrides_cache() -> None:
    set_capabilities(_caps(width=40))
    assert get_capabilities().width == 40


def test_is_interactive_false_when_ci() -> None:
    set_capabilities(_caps(is_tty=True, is_ci=True))
    assert get_capabilities().is_interactive is False


def test_is_interactive_false_when_not_tty() -> None:
    set_capabilities(_caps(is_tty=False, is_ci=False))
    assert get_capabilities().is_interactive is False


def test_is_interactive_true_for_real_terminal() -> None:
    set_capabilities(_caps(is_tty=True, is_ci=False))
    assert get_capabilities().is_interactive is True


def test_is_narrow() -> None:
    set_capabilities(_caps(width=60))
    assert get_capabilities().is_narrow is True
    set_capabilities(_caps(width=120))
    assert get_capabilities().is_narrow is False

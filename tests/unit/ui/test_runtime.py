from __future__ import annotations

from animax.ui.runtime import UiRuntimeState, configure, get_state, reset


def test_default_state() -> None:
    assert get_state() == UiRuntimeState()


def test_configure_updates_only_given_fields() -> None:
    configure(ascii_mode=True)
    state = get_state()
    assert state.ascii_mode is True
    assert state.animations_enabled is True  # untouched, still default

    configure(animations_enabled=False)
    state = get_state()
    assert state.ascii_mode is True  # still set from before
    assert state.animations_enabled is False


def test_reset_restores_defaults() -> None:
    configure(ascii_mode=True, animations_enabled=False, theme_name="light", debug=True)
    reset()
    assert get_state() == UiRuntimeState()

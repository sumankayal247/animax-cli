from __future__ import annotations

from animax.services.plugin_service import get_plugin_manager, reset_plugin_manager


def test_get_plugin_manager_returns_same_instance() -> None:
    first = get_plugin_manager()
    second = get_plugin_manager()

    assert first is second


def test_reset_plugin_manager_forces_a_new_instance() -> None:
    first = get_plugin_manager()
    reset_plugin_manager()
    second = get_plugin_manager()

    assert first is not second

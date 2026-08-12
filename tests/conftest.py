from __future__ import annotations

import pytest

from animax.services.plugin_service import reset_plugin_manager
from animax.ui import runtime as ui_runtime
from animax.ui.capabilities import reset_capabilities


@pytest.fixture(autouse=True)
def _reset_plugin_manager_singleton() -> None:
    """Each test gets a fresh PluginManager singleton.

    services.plugin_service.get_plugin_manager() is process-wide mutable
    state; without this, a manager built in one test (with whatever
    config paths were active then) would leak into the next.
    """
    reset_plugin_manager()


@pytest.fixture(autouse=True)
def _reset_ui_state() -> None:
    """Same story for ui.runtime's resolved state and the cached terminal
    capabilities snapshot — both process-wide, both need a clean slate.
    """
    ui_runtime.reset()
    reset_capabilities()

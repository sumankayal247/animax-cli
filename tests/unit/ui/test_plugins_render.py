from __future__ import annotations

from collections.abc import Callable

import animax.ui.plugins as plugins_module
from animax.models.plugin import (
    HealthStatus,
    PluginCategory,
    PluginInfo,
    PluginRecord,
    PluginSource,
    ProviderCapabilities,
)
from animax.ui.plugins import render_plugin_table


def _record() -> PluginRecord:
    info = PluginInfo(
        name="anilist",
        version="1.0.0",
        author="test",
        description="test",
        category=PluginCategory.METADATA,
        api_version="1.0.0",
        capabilities=ProviderCapabilities(search=True),
    )

    class _Dummy:
        pass

    return PluginRecord(
        info=info, instance=_Dummy(), source=PluginSource.BUILTIN, health=HealthStatus.HEALTHY
    )


def test_empty_registry_shows_message_not_a_table(capture_console: Callable[..., str]) -> None:
    out = capture_console(plugins_module, render_plugin_table, [])
    assert "No plugins discovered yet" in out


def test_populated_registry_shows_table(capture_console: Callable[..., str]) -> None:
    out = capture_console(plugins_module, render_plugin_table, [_record()])
    assert "anilist" in out
    assert "No plugins discovered yet" not in out

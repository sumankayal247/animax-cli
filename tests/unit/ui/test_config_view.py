from __future__ import annotations

from collections.abc import Callable

import animax.ui.config_view as config_view_module
from animax.config.schema import Settings
from animax.ui.config_view import render_config


def test_render_config_shows_default_status(capture_console: Callable[..., str]) -> None:
    settings = Settings()
    out = capture_console(config_view_module, render_config, settings)
    assert "General" in out
    assert "Player" in out
    assert "Download" in out
    assert "default" in out.lower()


def test_render_config_shows_modified_status(capture_console: Callable[..., str]) -> None:
    settings = Settings()
    settings.theme = "light"
    out = capture_console(config_view_module, render_config, settings)
    assert "modified" in out.lower()
    assert "light" in out

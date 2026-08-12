from __future__ import annotations

import pytest
import typer

from animax.ui.help import build_epilog, register_alias


def test_build_epilog_contains_version_and_paths() -> None:
    epilog = build_epilog()
    assert "animax-cli" in epilog
    assert "Config file" in epilog
    assert "Plugin dir" in epilog
    assert "ANIMAX_*" in epilog


def test_build_epilog_uses_double_newlines_between_lines() -> None:
    # Typer/Rich only preserves breaks at \n\n — a single \n would reflow
    # into one paragraph (see help.py's docstring on this).
    epilog = build_epilog()
    assert "\n\n" in epilog


def test_register_alias_adds_second_command_name() -> None:
    app = typer.Typer()

    @app.command()
    def original() -> None:
        pass

    register_alias(app, existing="original", alias="orig")

    names = set()
    for command_info in app.registered_commands:
        name = command_info.name or (
            command_info.callback.__name__.replace("_", "-") if command_info.callback else None
        )
        names.add(name)

    assert "orig" in names
    assert "original" in names


def test_register_alias_raises_for_unknown_command() -> None:
    app = typer.Typer()

    @app.command()
    def real() -> None:
        pass

    with pytest.raises(ValueError):
        register_alias(app, existing="does-not-exist", alias="x")

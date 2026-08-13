from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from animax.cli.app import app
from animax.config import paths as config_paths

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "animax-cli" in result.stdout


def test_about_command() -> None:
    result = runner.invoke(app, ["about"])
    assert result.exit_code == 0
    assert "Apache License 2.0" in result.stdout

def test_help_flag_shows_usage() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_plugins_command_runs() -> None:
    result = runner.invoke(app, ["plugins"])
    assert result.exit_code == 0


def test_doctor_all_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(config_paths, "config_dir", lambda: tmp_path / "config")
    monkeypatch.setattr(config_paths, "cache_dir", lambda: tmp_path / "cache")
    monkeypatch.setattr(config_paths, "data_dir", lambda: tmp_path / "data")
    monkeypatch.setattr(config_paths, "log_dir", lambda: tmp_path / "log")
    monkeypatch.setattr(config_paths, "database_file", lambda: tmp_path / "data" / "animax.db")

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "FAIL" not in result.stdout
    assert "Plugin manager" in result.stdout


def test_config_path_and_show(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(config_paths, "config_dir", lambda: tmp_path / "config")
    monkeypatch.setattr(config_paths, "config_file", lambda: tmp_path / "config" / "settings.toml")

    path_result = runner.invoke(app, ["config", "path"])
    assert path_result.exit_code == 0
    assert str(tmp_path) in path_result.stdout

    show_result = runner.invoke(app, ["config", "show"])
    assert show_result.exit_code == 0
    assert "schema_version" in show_result.stdout

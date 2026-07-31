from __future__ import annotations

from pathlib import Path

import pytest

from animax.config.loader import ensure_exists, load, save
from animax.config.schema import Settings
from animax.core.errors import ConfigError


def test_load_missing_file_returns_defaults(tmp_path: Path) -> None:
    settings = load(tmp_path / "settings.toml")
    assert settings == Settings()


def test_save_then_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    original = Settings()
    original.download.concurrent_downloads = 7
    original.theme = "midnight"

    save(original, path)
    loaded = load(path)

    assert loaded.download.concurrent_downloads == 7
    assert loaded.theme == "midnight"


def test_ensure_exists_creates_file_with_defaults(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "settings.toml"
    assert not path.exists()

    settings = ensure_exists(path)

    assert path.exists()
    assert settings == Settings()


def test_load_invalid_toml_raises_config_error(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text("not [ valid toml")

    with pytest.raises(ConfigError):
        load(path)

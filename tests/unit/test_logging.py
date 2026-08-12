import logging
from pathlib import Path

import pytest

from animax.logging_config import configure_logging, log_crash


def test_logging_config_creates_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("animax.logging_config.log_dir", lambda: tmp_path)

    # Reset handlers
    logging.getLogger().handlers = []

    configure_logging(debug=True, verbose=False)

    assert (tmp_path / "animax.log").exists()
    assert (tmp_path / "animax.json.log").exists()

    # Check that it captured something
    logging.getLogger(__name__).debug("Test message")

    content = (tmp_path / "animax.log").read_text(encoding="utf-8")
    assert "Test message" in content

    json_content = (tmp_path / "animax.json.log").read_text(encoding="utf-8")
    assert "Test message" in json_content
    assert '"level": "DEBUG"' in json_content


def test_log_crash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("animax.logging_config.log_dir", lambda: tmp_path)

    try:
        raise ValueError("Simulated crash")
    except Exception as e:
        log_crash(e)

    crash_file = tmp_path / "crash.log"
    assert crash_file.exists()
    content = crash_file.read_text(encoding="utf-8")
    assert "--- CRASH REPORT ---" in content
    assert "Simulated crash" in content
    assert "ValueError" in content

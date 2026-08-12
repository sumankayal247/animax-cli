from __future__ import annotations

from animax.ui.progress import build_indeterminate_progress, build_progress
from animax.ui.runtime import configure


def test_build_progress_basic() -> None:
    progress = build_progress()
    with progress:
        task = progress.add_task("working", total=10)
        progress.update(task, advance=5)
    assert progress.tasks[0].completed == 5


def test_build_progress_transfer_columns_present() -> None:
    progress = build_progress(transfer=True)
    column_types = {type(c).__name__ for c in progress.columns}
    assert "DownloadColumn" in column_types
    assert "TransferSpeedColumn" in column_types


def test_build_progress_no_spinner_when_animations_disabled() -> None:
    configure(animations_enabled=False)
    progress = build_progress()
    column_types = {type(c).__name__ for c in progress.columns}
    assert "SpinnerColumn" not in column_types


def test_build_progress_has_spinner_when_animations_enabled() -> None:
    configure(animations_enabled=True)
    progress = build_progress()
    column_types = {type(c).__name__ for c in progress.columns}
    assert "SpinnerColumn" in column_types


def test_build_indeterminate_progress_runs() -> None:
    progress = build_indeterminate_progress()
    with progress:
        progress.add_task("discovering plugins", total=None)

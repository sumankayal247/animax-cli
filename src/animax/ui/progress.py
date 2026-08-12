"""Reusable progress components: single, multi, spinner, transfer speed, ETA.

Nothing downloads yet (Phase 5) — these exist now so Phase 5 only needs to
call `add_task`/`update` against an already-designed component, per the
Phase 3 brief ("even though downloading isn't implemented yet, the
components should already exist").

Rich's `Progress`/`Live` already detect a non-terminal or CI output and
fall back to a reduced, non-animated render on their own — this module
doesn't duplicate that detection, it only decides *which columns* to show
based on `ui.runtime.animations_enabled` (dropping the spinner when
animations are off, since a spinner implies continuous redraw).
"""

from __future__ import annotations

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from animax.ui.console import console
from animax.ui.renderers.animations import DEFAULT_SPINNER
from animax.ui.runtime import get_state


def build_progress(*, transfer: bool = False) -> Progress:
    """A determinate progress bar: description, bar, percentage, elapsed, ETA.

    ``transfer=True`` adds byte-count and transfer-speed columns, for a
    download. Multiple tasks (`progress.add_task(...)` called more than
    once) render as multiple stacked bars — that's "multi progress" here;
    Rich has no native bar-within-a-bar nesting, so a "nested" step is
    conventionally a second task whose description is indented, e.g.
    ``"  ↳ verifying"`` — a visual cue, not a structural one.
    """
    columns: list[ProgressColumn] = [TextColumn("[progress.description]{task.description}")]
    if get_state().animations_enabled:
        columns.insert(0, SpinnerColumn(spinner_name=DEFAULT_SPINNER))
    columns += [BarColumn(), TaskProgressColumn()]
    if transfer:
        columns += [DownloadColumn(), TransferSpeedColumn()]
    columns += [TimeElapsedColumn(), TimeRemainingColumn()]
    return Progress(*columns, console=console)


def build_indeterminate_progress() -> Progress:
    """A spinner + description only, for operations of unknown length
    (e.g. plugin discovery). Falls back to a static description when
    animations are disabled, rather than a spinner that can't animate.
    """
    if get_state().animations_enabled:
        return Progress(
            SpinnerColumn(spinner_name=DEFAULT_SPINNER),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        )
    return Progress(TextColumn("[progress.description]{task.description}"), console=console)

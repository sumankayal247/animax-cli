"""Console logging setup.

This is the Phase 1 baseline: pretty console logs via Rich, toggled by
--debug. File logging, structured logging, and crash reports (per the
project's Logging requirements) are full Phase 2 deliverables tracked in
docs/Roadmap.md.
"""

from __future__ import annotations

import logging

from rich.logging import RichHandler

from animax.ui.theme import console


def configure_logging(*, debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=debug, show_path=debug)],
        force=True,
    )

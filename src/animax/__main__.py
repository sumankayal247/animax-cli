"""Top-level entrypoint: runs the Typer app and renders any escaping error nicely."""

from __future__ import annotations

import sys

from animax.cli.app import app
from animax.core.errors import AnimaxError
from animax.ui.errors import render_error, render_unexpected_error


def main() -> None:
    try:
        app()
    except AnimaxError as exc:
        render_error(exc)
        sys.exit(1)
    except Exception as exc:  # top-level safety net: never show a raw traceback
        render_unexpected_error(exc)
        sys.exit(1)


if __name__ == "__main__":
    main()

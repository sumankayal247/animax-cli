"""`anime doctor` — thin controller over services.doctor_service."""

from __future__ import annotations

import asyncio

import typer

from animax.services.doctor_service import run_checks
from animax.ui.doctor import render_doctor_results


def register(app: typer.Typer) -> None:
    @app.command()
    def doctor() -> None:
        """Diagnose your Animax-Cli installation and environment."""
        results = asyncio.run(run_checks())
        all_passed = render_doctor_results(results)
        raise typer.Exit(code=0 if all_passed else 1)

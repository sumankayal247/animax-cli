"""`anime doctor` — thin controller over services.doctor_service."""

from __future__ import annotations

import asyncio

import typer

from animax.services.doctor_service import run_checks
from animax.ui.doctor import render_doctor_results


def register(app: typer.Typer) -> None:
    @app.command()
    def doctor(
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Show details for passing checks."),
        json_output: bool = typer.Option(False, "--json", help="Output results as JSON."),
    ) -> None:
        """Diagnose your Animax-Cli installation and environment."""
        from animax.ui.doctor import render_doctor_json
        
        results = asyncio.run(run_checks())
        
        if json_output:
            all_passed = render_doctor_json(results)
        else:
            all_passed = render_doctor_results(results, verbose=verbose)
            
        raise typer.Exit(code=0 if all_passed else 1)

"""Renders `anime doctor` results as a Rich table."""

from __future__ import annotations

from rich.table import Table

from animax.installer.checks import CheckResult
from animax.ui.theme import console


def render_doctor_results(results: list[CheckResult]) -> bool:
    """Print the results table; returns True if every check passed."""
    table = Table(title="anime doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")

    all_passed = True
    for result in results:
        if result.passed:
            status = "[animax.success]OK[/]"
        else:
            all_passed = False
            status = "[animax.error]FAIL[/]"

        detail = result.detail
        if not result.passed and result.fix:
            detail += f"\n[animax.warning]Fix:[/] {result.fix}"

        table.add_row(result.name, status, detail)

    console.print(table)
    
    if all_passed:
        console.print(f"[animax.success]All {len(results)} checks passed[/]")
    else:
        console.print("[animax.warning]Recommendations[/]")
        
    return all_passed

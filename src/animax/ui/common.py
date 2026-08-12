"""Small, reusable print helpers every command reaches for instead of
hand-rolling Rich markup inline. One line each, on purpose — these are the
building blocks commands compose, not another abstraction layer over them.
"""

from __future__ import annotations

from collections.abc import Iterable

from rich.rule import Rule
from rich.text import Text

from animax.ui.console import console
from animax.ui.renderers import styles
from animax.ui.renderers.icons import icon


def success(message: str) -> None:
    console.print(f"[{styles.SUCCESS}]{icon('success')} {message}[/]")


def warning(message: str) -> None:
    console.print(f"[{styles.WARNING}]{icon('warning')} {message}[/]")


def fatal(message: str) -> None:
    console.print(f"[{styles.ERROR}]{icon('error')} {message}[/]")


def info(message: str) -> None:
    console.print(f"[{styles.INFO}]{icon('info')} {message}[/]")


def tip(message: str) -> None:
    console.print(f"[{styles.MUTED}]Tip:[/] {message}")


def note(message: str) -> None:
    console.print(f"[{styles.MUTED}]Note:[/] {message}")


def next_steps(steps: Iterable[str]) -> None:
    """A short numbered "what to do next" list, e.g. after a command completes."""
    console.print(f"[{styles.TITLE}]Next steps[/]")
    for n, step in enumerate(steps, start=1):
        console.print(f"  {n}. {step}")


def bullet_list(items: Iterable[str]) -> None:
    for item in items:
        console.print(f"  {icon('bullet')} {item}")


def key_value(pairs: dict[str, str], *, key_style: str = styles.MUTED) -> None:
    """A simple aligned key: value block (not a table — for a handful of pairs,
    e.g. a version/about screen), padded to the longest key.
    """
    if not pairs:
        return
    width = max(len(k) for k in pairs)
    for key, value in pairs.items():
        console.print(f"[{key_style}]{key.rjust(width)}:[/] {value}")


def horizontal_rule(title: str | None = None) -> None:
    console.print(Rule(title, style=styles.MUTED) if title else Rule(style=styles.MUTED))


def section_header(title: str) -> None:
    console.print()
    console.print(f"[{styles.TITLE}]{title}[/]")


def badge(label: str, *, style: str = styles.ACCENT) -> Text:
    """A small inline `[ LABEL ]` badge — for embedding in a table cell/panel."""
    return Text(f" {label} ", style=f"reverse {style}")


def tag(label: str, *, style: str = styles.MUTED) -> str:
    """A lightweight inline tag as markup, e.g. for a table cell: `(tag)`."""
    return f"[{style}]({label})[/]"

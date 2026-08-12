"""Reusable interactive prompt helpers: confirm, select, multi-select, text,
password, path picker. Every one refuses to hang in a non-interactive
terminal (CI, piped output) — it raises a clear UiError instead, unless a
default was given.

No numbered-arrow-key menu library is added as a dependency — selection
is a numbered list + an integer prompt, which works over plain stdin
everywhere (SSH, CI-with-input, redirected terminals) without needing
raw-mode terminal control. See docs/Architecture.md for why this project
stays dependency-minimal.
"""

from __future__ import annotations

from pathlib import Path

from rich.prompt import Confirm, IntPrompt, Prompt

from animax.core.errors import UiError
from animax.ui.capabilities import get_capabilities
from animax.ui.console import console


def _require_interactive(prompt: str) -> None:
    if not get_capabilities().is_interactive:
        raise UiError(
            f"Can't prompt for input: {prompt!r}",
            reason="Not an interactive terminal (redirected input, or CI detected).",
            fix="Pass the value as a flag/argument instead, or provide a default.",
        )


def confirm(question: str, *, default: bool = True) -> bool:
    if not get_capabilities().is_interactive:
        return default
    return Confirm.ask(question, default=default, console=console)


def text(prompt: str, *, default: str | None = None, password: bool = False) -> str:
    if not get_capabilities().is_interactive:
        if default is not None:
            return default
        _require_interactive(prompt)
    if default is not None:
        return Prompt.ask(prompt, default=default, password=password, console=console)
    return Prompt.ask(prompt, password=password, console=console)


def password(prompt: str) -> str:
    _require_interactive(prompt)
    return Prompt.ask(prompt, password=True, console=console)


def select[T](prompt: str, choices: list[T], *, labels: list[str] | None = None) -> T:
    """Numbered-list selection. ``labels`` defaults to ``str(choice)`` per choice."""
    if not choices:
        raise UiError(f"Can't prompt {prompt!r}: no choices available.")
    display = labels or [str(c) for c in choices]
    if not get_capabilities().is_interactive:
        return choices[0]
    console.print(f"[animax.title]{prompt}[/]")
    for i, label in enumerate(display, start=1):
        console.print(f"  {i}. {label}")
    index = IntPrompt.ask(
        "Enter a number",
        choices=[str(i) for i in range(1, len(choices) + 1)],
        console=console,
    )
    return choices[index - 1]


def multiselect[T](prompt: str, choices: list[T], *, labels: list[str] | None = None) -> list[T]:
    """Comma-separated numbered selection, e.g. "1,3,4"."""
    if not choices:
        raise UiError(f"Can't prompt {prompt!r}: no choices available.")
    display = labels or [str(c) for c in choices]
    if not get_capabilities().is_interactive:
        return []
    console.print(f"[animax.title]{prompt}[/] [animax.muted](comma-separated numbers)[/]")
    for i, label in enumerate(display, start=1):
        console.print(f"  {i}. {label}")
    raw = Prompt.ask("Enter numbers", console=console)
    indices = {int(part.strip()) for part in raw.split(",") if part.strip().isdigit()}
    return [choices[i - 1] for i in sorted(indices) if 1 <= i <= len(choices)]


def path_picker(prompt: str, *, must_exist: bool = False, default: Path | None = None) -> Path:
    if not get_capabilities().is_interactive:
        if default is not None:
            return default
        _require_interactive(prompt)
    while True:
        raw = (
            Prompt.ask(prompt, default=str(default), console=console)
            if default is not None
            else Prompt.ask(prompt, console=console)
        )
        candidate = Path(raw).expanduser()
        if must_exist and not candidate.exists():
            console.print(f"[animax.warning]{candidate} doesn't exist.[/]")
            continue
        return candidate

"""A reusable menu framework: a titled list of choices, rendered as a
table, driven by a numbered selection prompt.

Framework only — no wiring to real data yet. This is what will power the
provider manager, configuration editor, episode selection, search
results, library, and history browsers once those commands exist
(Phase 4/5/6); today it's exercised only by its own tests plus anything
that wants a generic "pick one of these" flow.
"""

from __future__ import annotations

from dataclasses import dataclass

from animax.ui.console import console
from animax.ui.prompts import select
from animax.ui.tables import build_table


@dataclass(frozen=True, slots=True)
class MenuItem:
    label: str
    value: str
    description: str = ""


class Menu:
    """A titled, numbered list of `MenuItem`s."""

    def __init__(self, title: str, items: list[MenuItem]) -> None:
        self.title = title
        self.items = items

    def render(self) -> None:
        table = build_table(
            self.title,
            ("#", "Option", "Description"),
            ((str(i), item.label, item.description) for i, item in enumerate(self.items, start=1)),
            justify=("right", "left", "left"),
        )
        console.print(table)

    def choose(self) -> MenuItem:
        """Render the menu, then prompt for one choice."""
        self.render()
        labels = [item.label for item in self.items]
        return select("Choose an option", self.items, labels=labels)

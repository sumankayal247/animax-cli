"""A grouped status tree: title -> named groups -> status-labeled leaves.

Used by `ui.doctor` today ("Environment" / "Plugins" groups); the same
shape fits the "Metadata Providers" / "Download Providers" per-category
health breakdown planned for Phase 4/5 (docs/Installer.md "Planned").
"""

from __future__ import annotations

from dataclasses import dataclass

from rich.tree import Tree

from animax.ui.status import StatusKind, status_markup


@dataclass(frozen=True, slots=True)
class TreeEntry:
    label: str
    kind: StatusKind
    detail: str = ""


def build_status_tree(title: str, groups: dict[str, list[TreeEntry]]) -> Tree:
    tree = Tree(f"[animax.title]{title}[/]")
    for group_name, entries in groups.items():
        branch = tree.add(f"[animax.muted]{group_name}[/]")
        for entry in entries:
            line = status_markup(entry.kind, entry.label)
            if entry.detail:
                line += f"  [animax.muted]{entry.detail}[/]"
            branch.add(line)
    return tree

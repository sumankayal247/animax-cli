from __future__ import annotations

from animax.ui.widgets.tree import TreeEntry, build_status_tree


def test_build_status_tree_structure() -> None:
    tree = build_status_tree(
        "anime doctor",
        {
            "Checks": [
                TreeEntry(label="Python", kind="success", detail="3.12"),
                TreeEntry(label="Database", kind="error", detail="locked"),
            ]
        },
    )
    # Rich's Tree exposes children as .children, one per top-level group.
    assert len(tree.children) == 1
    group = tree.children[0]
    assert len(group.children) == 2

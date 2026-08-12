from __future__ import annotations

from animax.ui.capabilities import TerminalCapabilities, set_capabilities
from animax.ui.menus import Menu, MenuItem


def test_menu_render_does_not_raise() -> None:
    menu = Menu("Providers", [MenuItem(label="AniList", value="anilist", description="Metadata")])
    menu.render()


def test_menu_choose_returns_first_item_when_not_interactive() -> None:
    set_capabilities(
        TerminalCapabilities(
            width=100,
            height=24,
            is_tty=False,
            is_ci=False,
            supports_color=True,
            supports_unicode=True,
            platform_name="Linux",
        )
    )
    items = [MenuItem(label="A", value="a"), MenuItem(label="B", value="b")]
    menu = Menu("Choices", items)
    assert menu.choose() is items[0]

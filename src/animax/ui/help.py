"""Builds the root app's help epilog and command-category/alias wiring.

Typer already renders `--help` with Rich (panels, colored usage) by
default — this module adds the extra polish the Phase 3 brief asks for on
top of that default: environment variables, config/plugin-dir paths,
version, and a couple of common-workflow examples, all in one epilog
block; plus category grouping (`rich_help_panel`) and alias registration,
used from `cli.app`.
"""

from __future__ import annotations

import typer

from animax import __version__
from animax.config.paths import config_file, user_plugin_dir
from animax.core.constants import APP_NAME, COMMAND_NAME

#: rich_help_panel names, applied per-command in cli.app._COMMAND_MODULES.
#: Centralized here so the category list itself has one home.
CATEGORY_CONTENT = "Content"
CATEGORY_SYSTEM = "System"
CATEGORY_INFO = "Info"


def build_epilog() -> str:
    """The block shown at the bottom of `anime --help`.

    Typer/Rich collapses single newlines within one epilog "paragraph"
    into spaces and only preserves breaks at *double* newlines (see
    typer.rich_utils.rich_format_help) — so each line below that needs to
    stay on its own line is its own \\n\\n-separated paragraph, not just
    \\n-separated.
    """
    return "\n\n".join(
        [
            f"[bold]{APP_NAME}[/bold] v{__version__}",
            "[bold]Common workflows[/bold]",
            f"{COMMAND_NAME} doctor        Check your installation is healthy",
            f"{COMMAND_NAME} plugins       See what's discovered and enabled",
            f"{COMMAND_NAME} config show   View the resolved configuration",
            "[bold]Environment variables[/bold]",
            "ANIMAX_*    Override any config value (see config show)",
            "NO_COLOR    Disable colored output",
            "[bold]Paths[/bold]",
            f"Config file:  {config_file()}",
            f"Plugin dir:   {user_plugin_dir()}",
        ]
    )


def register_alias(app: typer.Typer, *, existing: str, alias: str) -> None:
    """Register ``alias`` as a second name for an already-registered command.

    Must be called after every module's register(app) has run. Raises if
    ``existing`` isn't a registered command name — fails loudly rather
    than silently no-op-ing on a typo.
    """
    registered = app.registered_commands
    for command_info in registered:
        effective_name = command_info.name or (
            command_info.callback.__name__.replace("_", "-") if command_info.callback else None
        )
        if effective_name == existing:
            app.registered_commands.append(
                command_info.__class__(
                    name=alias,
                    cls=command_info.cls,
                    context_settings=command_info.context_settings,
                    callback=command_info.callback,
                    help=command_info.help,
                    epilog=command_info.epilog,
                    short_help=f"Alias for '{existing}'.",
                    hidden=True,
                    rich_help_panel=command_info.rich_help_panel,
                )
            )
            return
    raise ValueError(f"Cannot alias unknown command {existing!r}")

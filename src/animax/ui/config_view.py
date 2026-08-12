"""The Configuration Viewer: grouped sections, current vs. default values,
and which fields have been overridden — a beautiful `anime config show`,
not just a JSON dump.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from animax.config.schema import Settings
from animax.ui.console import console
from animax.ui.status import status_markup
from animax.ui.tables import build_table

#: Top-level scalar fields shown under "General" — the nested sub-model
#: fields (player, download, ...) get their own section table instead.
_GENERAL_FIELDS = ("schema_version", "theme", "language")


def _diff_fields(
    current: BaseModel, default: BaseModel, *, fields: tuple[str, ...] | None = None
) -> list[tuple[str, Any, Any, bool]]:
    field_names = fields or tuple(type(current).model_fields)
    rows = []
    for field in field_names:
        current_value = getattr(current, field)
        default_value = getattr(default, field)
        rows.append((field, current_value, default_value, current_value != default_value))
    return rows


def _section_table(
    title: str, model: BaseModel, default_model: BaseModel, *, fields: tuple[str, ...] | None = None
) -> Any:
    rows = []
    for field, current_value, default_value, modified in _diff_fields(
        model, default_model, fields=fields
    ):
        marker = (
            status_markup("warning", "modified")
            if modified
            else status_markup("success", "default")
        )
        rows.append((field, str(current_value), str(default_value), marker))
    return build_table(title, ("Field", "Current", "Default", "Status"), rows)


def render_config(settings: Settings) -> None:
    """Print every configuration section as a grouped, diffed table."""
    defaults = Settings()

    console.print(_section_table("General", settings, defaults, fields=_GENERAL_FIELDS))
    for section in ("player", "download", "plugins", "cache", "logging"):
        model = getattr(settings, section)
        default_model = getattr(defaults, section)
        console.print(_section_table(section.title(), model, default_model))

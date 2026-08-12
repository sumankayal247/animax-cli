"""Named style-string constants for the theme keys in ui.theme's palettes.

Renderers reference these constants instead of typing the string
literal ("animax.success") inline, so a typo is a NameError at import
time instead of a silently-ignored unknown style at render time.
"""

from __future__ import annotations

TITLE = "animax.title"
ACCENT = "animax.accent"
SUCCESS = "animax.success"
WARNING = "animax.warning"
ERROR = "animax.error"
INFO = "animax.info"
MUTED = "animax.muted"

STATUS_PENDING = "animax.status.pending"
STATUS_RUNNING = "animax.status.running"
STATUS_DONE = "animax.status.done"
STATUS_FAILED = "animax.status.failed"

DOWNLOAD_ACTIVE = "animax.download.active"
DOWNLOAD_PAUSED = "animax.download.paused"
DOWNLOAD_DONE = "animax.download.done"
DOWNLOAD_FAILED = "animax.download.failed"

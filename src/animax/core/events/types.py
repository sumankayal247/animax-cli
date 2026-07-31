"""Well-known event names published on the default event bus.

Payload shapes are documented per-event here rather than enforced with a
class hierarchy, to keep the bus lightweight — see docs/Architecture.md
for the event catalogue as it grows.
"""

from __future__ import annotations

PLUGIN_LOADED = "plugin.loaded"
"""payload: models.plugin.PluginRecord"""

PLUGIN_DISABLED = "plugin.disabled"
"""payload: models.plugin.PluginRecord"""

PLUGIN_HEALTH_CHANGED = "plugin.health_changed"
"""payload: models.plugin.PluginRecord"""

DOWNLOAD_QUEUED = "download.queued"
"""payload: models.download.DownloadTask"""

DOWNLOAD_PROGRESS = "download.progress"
"""payload: models.download.DownloadTask"""

DOWNLOAD_COMPLETED = "download.completed"
"""payload: models.download.DownloadTask"""

DOWNLOAD_FAILED = "download.failed"
"""payload: models.download.DownloadTask"""

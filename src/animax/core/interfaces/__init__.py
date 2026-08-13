"""Abstract plugin interfaces. The core app depends only on these, never on
concrete provider implementations under animax.plugins.*.
"""

from typing import cast

from animax.core.interfaces.authentication import AuthenticationPlugin
from animax.core.interfaces.base import BasePlugin
from animax.core.interfaces.download import DownloadPlugin
from animax.core.interfaces.metadata import MetadataPlugin
from animax.core.interfaces.notification import NotificationLevel, NotificationPlugin
from animax.core.interfaces.player import PlayerPlugin
from animax.core.interfaces.search import SearchPlugin
from animax.core.interfaces.source import SourcePlugin
from animax.core.interfaces.streaming import StreamingPlugin

__all__ = [
    "AuthenticationPlugin",
    "BasePlugin",
    "DownloadPlugin",
    "MetadataPlugin",
    "NotificationLevel",
    "NotificationPlugin",
    "PlayerPlugin",
    "SearchPlugin",
    "SourcePlugin",
    "StreamingPlugin",
]

#: Maps a plugin category (models.plugin.PluginCategory value) to its ABC.
#: Used by the plugin manager to validate that a loaded plugin implements
#: the interface matching the category it declares in its PluginInfo. Every
#: value here is intentionally an abstract class — it is only ever used
#: with isinstance(), never instantiated directly — hence the cast.
CATEGORY_INTERFACES = cast(
    "dict[str, type[BasePlugin]]",
    {
        "metadata": MetadataPlugin,
        "download": DownloadPlugin,
        "streaming": StreamingPlugin,
        "player": PlayerPlugin,
        "notification": NotificationPlugin,
        "authentication": AuthenticationPlugin,
        "search": SearchPlugin,
        "source": SourcePlugin,
    },
)

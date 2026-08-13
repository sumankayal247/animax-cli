"""Abstract plugin interfaces. The core app depends only on these, never on
concrete provider implementations under animax.plugins.*.
"""

from typing import cast

from animax.core.interfaces.authentication import AuthenticationProvider
from animax.core.interfaces.base import BasePlugin
from animax.core.interfaces.download import DownloadProvider
from animax.core.interfaces.metadata import MetadataProvider
from animax.core.interfaces.notification import NotificationLevel, NotificationProvider
from animax.core.interfaces.player import PlayerProvider
from animax.core.interfaces.provider import BaseProvider
from animax.core.interfaces.search import SearchProvider
from animax.core.interfaces.source import SourceProvider
from animax.core.interfaces.streaming import StreamingProvider

__all__ = [
    "AuthenticationProvider",
    "BasePlugin",
    "BaseProvider",
    "DownloadProvider",
    "MetadataProvider",
    "NotificationLevel",
    "NotificationProvider",
    "PlayerProvider",
    "SearchProvider",
    "SourceProvider",
    "StreamingProvider",
]

CATEGORY_INTERFACES = cast(
    "dict[str, type[BaseProvider]]",
    {
        "metadata": MetadataProvider,
        "download": DownloadProvider,
        "streaming": StreamingProvider,
        "player": PlayerProvider,
        "notification": NotificationProvider,
        "authentication": AuthenticationProvider,
        "search": SearchProvider,
        "source": SourceProvider,
    },
)

"""Interface for notification plugins (desktop notifications, webhooks, ...)."""

from __future__ import annotations

from abc import abstractmethod
from enum import StrEnum

from animax.core.interfaces.base import BasePlugin


class NotificationLevel(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationPlugin(BasePlugin):
    """Delivers a notification to the user through some external channel."""

    @abstractmethod
    async def notify(self, title: str, message: str, *, level: NotificationLevel) -> None:
        raise NotImplementedError

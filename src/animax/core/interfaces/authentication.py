"""Interface for authentication plugins (per-provider login/session handling)."""

from __future__ import annotations

from abc import abstractmethod

from animax.core.interfaces.base import BasePlugin


class AuthenticationPlugin(BasePlugin):
    """Manages login/session state for a provider that requires authentication."""

    @abstractmethod
    async def is_authenticated(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def login(self, **credentials: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def logout(self) -> None:
        raise NotImplementedError

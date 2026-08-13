"""Base provider interface. Every provider category's ABC inherits from this."""

from __future__ import annotations

from abc import ABC, abstractmethod

from animax.models.provider import ProviderInfo


class BaseProvider(ABC):
    """Common contract every Animax-Cli provider must implement."""

    @property
    @abstractmethod
    def info(self) -> ProviderInfo:
        """Static metadata this provider declares about itself."""
        raise NotImplementedError

    async def setup(self) -> None:
        """Called once after the provider is loaded and validated."""
        return None

    async def teardown(self) -> None:
        """Called on shutdown or when the provider is disabled at runtime."""
        return None

    async def check_health(self) -> bool:
        """Report this provider's current health."""
        return True

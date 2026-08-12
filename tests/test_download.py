"""Tests for download service."""
import pytest

from animax.services.download_service import DownloadEngine


@pytest.mark.asyncio
async def test_download_engine() -> None:
    engine = DownloadEngine()
    assert engine is not None

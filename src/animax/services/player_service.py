"""Service for coordinating media playback."""

from __future__ import annotations

import logging
from typing import cast

from animax.core.interfaces.player import PlayerProvider
from animax.models.provider import ProviderCategory
from animax.models.plugin import PluginCategory
from animax.services.plugin_service import discover_plugins, get_provider_registry

logger = logging.getLogger(__name__)

async def play_media(target: str, resume_at_seconds: float | None = None, preferred_player: str | None = None) -> None:
    """Find an available player plugin and play the target."""
    pm = get_provider_registry()
    await discover_plugins()
    
    player: PlayerProvider | None = None
    
    if preferred_player:
        record = pm.get(preferred_player)
        if record and record.info.category == ProviderCategory.PLAYER and record.enabled:
            candidate = cast(PlayerProvider, record.instance)
            if candidate.is_available():
                player = candidate
    
    if not player:
        # Get all enabled player plugins sorted by priority
        players = pm.enabled(category=ProviderCategory.PLAYER)
        players.sort(key=lambda p: p.info.priority)
        
        for record in players:
            candidate = cast(PlayerProvider, record.instance)
            if candidate.is_available():
                player = candidate
                break
                
    if not player:
        raise RuntimeError("No available media player found. Install mpv or VLC.")
        
    logger.info(f"Using player plugin '{player.info.name}' for {target}")
    await player.play(target, resume_at_seconds=resume_at_seconds)

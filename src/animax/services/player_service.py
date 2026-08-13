"""Service for coordinating media playback."""

from __future__ import annotations

import logging
from typing import cast

from animax.core.interfaces.player import PlayerPlugin
from animax.services.plugin_service import get_plugin_manager, discover_plugins
from animax.models.plugin import PluginCategory

logger = logging.getLogger(__name__)

async def play_media(target: str, resume_at_seconds: float | None = None, preferred_player: str | None = None) -> None:
    """Find an available player plugin and play the target."""
    pm = get_plugin_manager()
    await discover_plugins()
    
    player: PlayerPlugin | None = None
    
    if preferred_player:
        record = pm.get(preferred_player)
        if record and record.info.category == PluginCategory.PLAYER and record.enabled:
            candidate = cast(PlayerPlugin, record.instance)
            if candidate.is_available():
                player = candidate
    
    if not player:
        # Get all enabled player plugins sorted by priority
        players = pm.enabled(category=PluginCategory.PLAYER)
        players.sort(key=lambda p: p.info.priority)
        
        for record in players:
            candidate = cast(PlayerPlugin, record.instance)
            if candidate.is_available():
                player = candidate
                break
                
    if not player:
        raise RuntimeError("No available media player found. Install mpv or VLC.")
        
    logger.info(f"Using player plugin '{player.info.name}' for {target}")
    await player.play(target, resume_at_seconds=resume_at_seconds)

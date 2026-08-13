from animax.core.interfaces.base import BasePlugin
from animax.models.plugin import PluginInfo, PluginCategory
from animax.models.provider import ProviderRecord
from animax.models.plugin import PluginSource
from animax.core.plugin_manager import PluginManager
from animax.core.provider_registry import ProviderRegistry

# Import all built-in providers
from animax.plugins.metadata.anilist import AniListProvider
from animax.plugins.metadata.kitsu import KitsuProvider
from animax.plugins.metadata.cinemeta import CinemetaProvider
from animax.plugins.search.nyaa import NyaaProvider
from animax.plugins.search.x1337x import Torrent1337xProvider
from animax.plugins.search.thepiratebay import ThePirateBayProvider
from animax.plugins.search.animetosho import AnimeToshoProvider
from animax.plugins.search.torrentgalaxy import TorrentGalaxyProvider
from animax.plugins.players.mpv import MPVPlayerProvider as MpvProvider
from animax.plugins.players.vlc import VLCPlayerProvider as VlcProvider

class BuiltinPlugin(BasePlugin):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="animax_builtin",
            description="Core built-in providers for Animax.",
            category=PluginCategory.GENERIC,
            version="1.0.0",
            author="animax",
            api_version="1.0.0"
        )

    async def setup(self, manager: PluginManager, registry: ProviderRegistry) -> None:
        providers = [
            AniListProvider(),
            KitsuProvider(),
            CinemetaProvider(),
            NyaaProvider(),
            Torrent1337xProvider(),
            ThePirateBayProvider(),
            AnimeToshoProvider(),
            TorrentGalaxyProvider(),
            MpvProvider(),
            VlcProvider(),
        ]
        
        for p in providers:
            record = ProviderRecord(
                info=p.info,
                instance=p,
                plugin_name=self.info.name,
                enabled=True,
                health=ProviderRecord.model_fields['health'].default
            )
            registry.register(record)

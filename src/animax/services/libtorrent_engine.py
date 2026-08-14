"""Libtorrent engine for streaming and downloading natively via uTP."""

import libtorrent as lt
import time
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LibtorrentEngine:
    def __init__(self):
        # Force uTP and encryption to evade ISP blocking
        self.settings = {
            'enable_outgoing_utp': True,
            'enable_incoming_utp': True,
            'enable_outgoing_tcp': False,
            'enable_incoming_tcp': False,
            'in_enc_policy': 1,  # 1 = forced encryption
            'out_enc_policy': 1,
            'listen_interfaces': '0.0.0.0:6881'
        }
        self.session = lt.session(self.settings)

    async def download(self, magnet_url: str, dest_dir: str, sequential: bool = False):
        params = lt.parse_magnet_uri(magnet_url)
        params.save_path = dest_dir
        
        handle = self.session.add_torrent(params)
        
        if sequential:
            handle.set_sequential_download(True)
            
        logger.info("Starting libtorrent engine...")
        
        while not handle.has_metadata():
            await asyncio.sleep(1)
            
        logger.info(f"Metadata fetched. Torrent: {handle.status().name}")
        
    async def stream(self, magnet_url: str, dest_dir: str, player: str = "vlc"):
        import subprocess
        params = lt.parse_magnet_uri(magnet_url)
        params.save_path = dest_dir
        
        handle = self.session.add_torrent(params)
        handle.set_sequential_download(True)
            
        logger.info("[yellow]Starting Libtorrent Engine with strict uTP and Encryption...[/yellow]")
        
        # Wait for metadata
        while not handle.has_metadata():
            await asyncio.sleep(1)
            
        torrent_info = handle.get_torrent_info()
        logger.info(f"[cyan]Metadata fetched![/cyan] Downloading: {torrent_info.name()}")
        
        # Find the largest file (the video)
        largest_file = max(range(torrent_info.num_files()), key=lambda i: torrent_info.files().file_size(i))
        file_path = Path(dest_dir) / torrent_info.files().file_path(largest_file)
        
        # Wait for 1% buffer to ensure the header is written
        logger.info("[yellow]Buffering video header...[/yellow]")
        while handle.status().progress < 0.01:
            s = handle.status()
            print(f"Buffering: {s.progress * 100:.2f}% | Peers: {s.num_peers} | Speed: {s.download_rate / 1000:.1f} kB/s", end='\r')
            await asyncio.sleep(1)
            
        print() # Newline after buffer
        logger.info(f"[green]Buffer complete! Launching {player}...[/green]")
        
        # Launch player directly on the file
        cmd = [player, str(file_path.absolute())]
        if player == "vlc":
            cmd.append("--fullscreen")
            
        player_proc = subprocess.Popen(cmd)
        
        # Keep downloading in background while player is open
        try:
            while player_proc.poll() is None:
                s = handle.status()
                print(f"Streaming: {s.progress * 100:.2f}% | Peers: {s.num_peers} | Speed: {s.download_rate / 1000:.1f} kB/s", end='\r')
                await asyncio.sleep(2)
        except KeyboardInterrupt:
            pass
        finally:
            print("\nShutting down stream...")
            if player_proc.poll() is None:
                player_proc.terminate()
            self.session.remove_torrent(handle)

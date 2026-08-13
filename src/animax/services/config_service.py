"""Business logic around loading and resolving configuration."""

from __future__ import annotations

from pathlib import Path

from animax.config.loader import ensure_exists
from animax.config.schema import Settings


def load_settings() -> Settings:
    return ensure_exists()

def update_setting(key: str, value: str) -> None:
    import tomllib
    import tomli_w
    from animax.config.paths import config_file
    
    path = config_file()
    if not path.exists():
        ensure_exists()
        
    doc = tomllib.loads(path.read_text())
    
    parts = key.split(".")
    current = doc
    
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
        
    last = parts[-1]
    
    # Try converting value to native type
    if value.lower() in ("true", "yes"):
        val = True
    elif value.lower() in ("false", "no"):
        val = False
    elif value.isdigit():
        val = int(value)
    else:
        try:
            val = float(value)
        except ValueError:
            val = value
            
    current[last] = val
    path.write_text(tomli_w.dumps(doc))


def resolve_download_directory(settings: Settings, cwd: Path) -> Path:
    """Downloads default to the current working directory unless overridden.

    E.g. running `anime download` from inside ~/Anime downloads there,
    unless download.directory is set in configuration.
    """
    if settings.download.directory:
        return Path(settings.download.directory).expanduser()
    return cwd

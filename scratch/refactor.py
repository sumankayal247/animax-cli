import os
import pathlib
import re

def main():
    base = pathlib.Path("src/animax")
    
    # 1. Rename PluginCategory to ProviderCategory in models/plugin.py
    models_plugin = base / "models" / "plugin.py"
    content = models_plugin.read_text()
    content = content.replace("PluginCategory", "ProviderCategory")
    models_plugin.write_text(content)

    # 2. In core/interfaces/base.py, rename BasePlugin to BaseProvider
    interfaces_base = base / "core" / "interfaces" / "base.py"
    content = interfaces_base.read_text()
    content = content.replace("BasePlugin", "BaseProvider")
    interfaces_base.write_text(content)

    # 3. In core/interfaces/metadata.py, rename MetadataPlugin to MetadataProvider
    interfaces_meta = base / "core" / "interfaces" / "metadata.py"
    content = interfaces_meta.read_text()
    content = content.replace("MetadataPlugin", "MetadataProvider")
    content = content.replace("BasePlugin", "BaseProvider")
    interfaces_meta.write_text(content)

    # 4. In plugins/metadata/anilist.py and kitsu.py
    for p in (base / "plugins" / "metadata").glob("*.py"):
        content = p.read_text()
        content = content.replace("MetadataPlugin", "MetadataProvider")
        content = content.replace("PluginCategory", "ProviderCategory")
        p.write_text(content)

    # 5. In core/plugin_manager.py
    pm = base / "core" / "plugin_manager.py"
    content = pm.read_text()
    content = content.replace("BasePlugin", "BaseProvider")
    content = content.replace("ProviderLoadedEvent", "ProviderLoadedEvent")
    pm.write_text(content)
    
    # Run tests to see where it breaks
    os.system("uv run pytest > tests_output.txt 2>&1")

if __name__ == "__main__":
    main()

import os
import glob

# A simple script to perform the Phase 4B refactor.

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # 1. Update models/plugin.py
    models_plugin = read('src/animax/models/plugin.py')
    models_plugin = models_plugin.replace('class PluginCategory', 'class ProviderCategory')
    models_plugin = models_plugin.replace('PluginCategory', 'ProviderCategory')
    models_plugin = models_plugin.replace('class PluginInfo', 'class ProviderInfo')
    models_plugin = models_plugin.replace('PluginInfo', 'ProviderInfo')
    models_plugin = models_plugin.replace('class PluginRecord', 'class ProviderRecord')
    models_plugin = models_plugin.replace('PluginRecord', 'ProviderRecord')
    models_plugin = models_plugin.replace('from animax.core.interfaces.base import BasePlugin', 'from animax.core.interfaces.base import BaseProvider')
    models_plugin = models_plugin.replace('def plugin(self) -> BasePlugin:\n        return cast("BasePlugin", self.instance)', 'def provider(self) -> BaseProvider:\n        return cast("BaseProvider", self.instance)')
    write('src/animax/models/plugin.py', models_plugin)
    
    # 2. Update interfaces
    for p in glob.glob('src/animax/core/interfaces/*.py'):
        content = read(p)
        content = content.replace('PluginCategory', 'ProviderCategory')
        content = content.replace('PluginInfo', 'ProviderInfo')
        content = content.replace('BasePlugin', 'BaseProvider')
        content = content.replace('MetadataPlugin', 'MetadataProvider')
        content = content.replace('SearchPlugin', 'SearchProvider')
        content = content.replace('class BaseProvider(ABC):', 'class BaseProvider(ABC):')
        write(p, content)

    # Note: I should rename the classes in the interfaces too.
    # We will do that with sed or more python replacements.
    print("Done")

if __name__ == '__main__':
    main()

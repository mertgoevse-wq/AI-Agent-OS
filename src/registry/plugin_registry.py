"""Registry for managing active plugins."""

from typing import Dict, List
import logging

from src.core.plugin import BasePlugin
from src.registry.plugin_loader import PluginLoader
from src.schemas.plugin_schema import PluginDefinition

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Manages loaded plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, BasePlugin] = {}
        self._definitions: Dict[str, PluginDefinition] = {}
        self.loader = PluginLoader()

    def register(self, plugin: BasePlugin, definition: PluginDefinition) -> None:
        """Register an active plugin instance."""
        name = definition.metadata.name
        if name in self._plugins:
            logger.warning("Plugin '%s' is already registered. Overwriting.", name)
        self._plugins[name] = plugin
        self._definitions[name] = definition
        logger.info("Registered plugin: %s v%s", name, definition.metadata.version)

    def get_plugin(self, name: str) -> BasePlugin | None:
        """Retrieve an active plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> List[PluginDefinition]:
        """List all registered plugin definitions."""
        return list(self._definitions.values())

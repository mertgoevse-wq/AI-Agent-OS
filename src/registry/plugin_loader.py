"""Loader for external plugins."""

from pathlib import Path
import yaml
import importlib
import sys

from src.schemas.plugin_schema import PluginDefinition, PluginMetadata


class PluginLoader:
    """Parses plugin.yaml files and loads plugin modules dynamically."""

    def load_plugin_manifest(self, file_path: str | Path) -> PluginDefinition:
        """Parse a plugin.yaml file into a PluginDefinition."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Plugin manifest not found: {file_path}")

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        
        meta_data = data.get("metadata", {})
        metadata = PluginMetadata(
            name=meta_data.get("name", path.parent.name),
            version=str(meta_data.get("version", "0.1.0")),
            description=meta_data.get("description", ""),
            author=meta_data.get("author", ""),
            dependencies=meta_data.get("dependencies", []),
        )

        return PluginDefinition(
            metadata=metadata,
            entry_point=data.get("entry_point", ""),
            config=data.get("config", {}),
        )

    def load_plugin_class(self, definition: PluginDefinition) -> type:
        """Dynamically import and return the plugin class based on entry_point."""
        entry = definition.entry_point
        if ":" not in entry:
            raise ValueError(f"Invalid entry_point format in {definition.metadata.name}: must be 'module:ClassName'")

        module_path, class_name = entry.split(":", 1)

        # Add current working directory to sys.path so dynamic imports work from workspace root
        cwd = str(Path.cwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)

        try:
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)
            return plugin_class
        except Exception as e:
            raise RuntimeError(f"Failed to load plugin {definition.metadata.name}: {e}") from e

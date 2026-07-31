"""Plugin schema for AI-Agent-OS."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PluginMetadata(BaseModel):
    """Metadata describing a downstream plugin."""
    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: List[str] = Field(default_factory=list)


class PluginDefinition(BaseModel):
    """Schema for plugin.yaml manifest files."""
    metadata: PluginMetadata
    entry_point: str  # e.g., "my_plugin.module:PluginClass"
    config: Dict[str, Any] = Field(default_factory=dict)

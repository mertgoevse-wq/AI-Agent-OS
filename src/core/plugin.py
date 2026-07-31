"""Base plugin interfaces for AI-Agent-OS."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from src.core.event import EventBus
from src.registry.agent_registry import AgentRegistry
from src.registry.skill_registry import SkillRegistry


class BasePlugin(ABC):
    """Abstract base class for all downstream plugins."""

    def __init__(
        self,
        event_bus: EventBus,
        agent_registry: AgentRegistry,
        skill_registry: SkillRegistry,
        config: Dict[str, Any],
    ) -> None:
        self.event_bus = event_bus
        self.agent_registry = agent_registry
        self.skill_registry = skill_registry
        self.config = config

    @abstractmethod
    async def initialize(self) -> None:
        """Called when the plugin is loaded into the kernel."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Called when the kernel is shutting down."""
        pass

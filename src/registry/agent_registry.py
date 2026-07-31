"""Agent Registry for AI-Agent-OS.

Manages registration and lookup of agent instances.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.agent import BaseAgent
from src.registry.agent_loader import AgentLoader, ConfiguredAgent
from src.schemas.agent_schema import AgentDefinition, ToolAccessLevel



class AgentRegistry:
    """Registry for managing agent instances and declarative definitions.

    Agents can be registered via instance or loaded from AGENT.md / YAML charter files.
    """

    def __init__(self, agents_dir: Optional[str] = None) -> None:
        self._agents: Dict[str, BaseAgent] = {}
        self._definitions: Dict[str, AgentDefinition] = {}
        self._agents_dir = agents_dir or "agents"
        self._loader = AgentLoader()

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent instance."""
        if agent.id in self._agents:
            raise ValueError(f"Agent '{agent.id}' is already registered")
        self._agents[agent.id] = agent
        if isinstance(agent, ConfiguredAgent):
            self._definitions[agent.id] = agent.definition

    def load_agent_from_file(self, file_path: str) -> BaseAgent:
        """Load an AGENT.md or YAML charter file and register the agent."""
        definition = self._loader.load_agent_file(file_path)
        agent_instance = self._loader.instantiate_agent(definition)
        self.register_agent(agent_instance)
        return agent_instance

    def scan_agents_directory(self) -> List[BaseAgent]:
        """Scan the agents directory for AGENT.md files and load them."""
        path = Path(self._agents_dir)
        if not path.exists():
            return []

        loaded_defs = self._loader.scan_directory(path)
        instances: List[BaseAgent] = []
        for defn in loaded_defs:
            if defn.id not in self._agents:
                agent = self._loader.instantiate_agent(defn)
                self.register_agent(agent)
                instances.append(agent)
        return instances

    def check_tool_permission(
        self,
        agent_id: str,
        tool_name: str,
        required_level: ToolAccessLevel = ToolAccessLevel.READ_ONLY,
    ) -> bool:
        """Verify if an agent has permission to execute a given tool.

        Rules:
        1. If tool is explicitly in denied_tools -> False.
        2. If allowed_tools is specified and tool matches -> True (provided level is allowed).
        3. If allowed_tools is empty -> True if required_level is in permissions.access_levels.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return False

        if not isinstance(agent, ConfiguredAgent):
            # Unconfigured agents default to allowed for backward compatibility
            return True

        policy = agent.permissions

        # Blacklist check
        for pattern in policy.denied_tools:
            if fnmatch.fnmatch(tool_name, pattern):
                return False

        # Access level check
        if required_level not in policy.access_levels:
            return False

        # Whitelist check
        if policy.allowed_tools:
            return any(fnmatch.fnmatch(tool_name, pat) for pat in policy.allowed_tools)

        return True

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get a registered agent by its ID."""
        return self._agents.get(agent_id)

    def get_definition(self, agent_id: str) -> Optional[AgentDefinition]:
        """Get declarative definition of an agent if available."""
        return self._definitions.get(agent_id)

    def list_agents(self) -> List[BaseAgent]:
        """List all registered agents."""
        return list(self._agents.values())

    def unregister_agent(self, agent_id: str) -> None:
        """Remove an agent from the registry."""
        self._agents.pop(agent_id, None)
        self._definitions.pop(agent_id, None)

    def has_agent(self, agent_id: str) -> bool:
        """Check if an agent is registered."""
        return agent_id in self._agents

    def count(self) -> int:
        """Return the number of registered agents."""
        return len(self._agents)
"""Agent Definition Loader for AI-Agent-OS.

Parses AGENT.md (Genesis_Harness format) and YAML manifests to construct
declarative AgentDefinition instances and configured BaseAgent instances.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from src.core.agent import BaseAgent
from src.core.task import Task
from src.schemas.agent_schema import AgentDefinition, PermissionPolicy, ToolAccessLevel
from src.schemas.common import AgentState


class ConfiguredAgent(BaseAgent):
    """A concrete BaseAgent initialized dynamically from an AgentDefinition charter."""

    def __init__(self, definition: AgentDefinition) -> None:
        super().__init__(
            agent_id=definition.id,
            name=definition.name,
            description=definition.description,
        )
        self.definition = definition
        self.system_prompt = definition.system_prompt
        self.permissions = definition.permissions

    async def initialize(self) -> None:
        self._set_state(AgentState.IDLE)

    async def execute(self, task: Task) -> Task:
        self._set_state(AgentState.RUNNING)
        # Execute task using configured prompt & skills
        task.complete(output=f"[{self.name} ({self.definition.role})] Processed: {task.input}")
        self._set_state(AgentState.IDLE)
        return task

    async def pause(self) -> None:
        self._set_state(AgentState.PAUSED)

    async def resume(self) -> None:
        self._set_state(AgentState.IDLE)

    async def terminate(self) -> None:
        self._set_state(AgentState.TERMINATED)


class AgentLoader:
    """Loader for reading and instantiating AgentDefinition objects from disk."""

    @classmethod
    def parse_frontmatter_markdown(cls, content: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter header and body from AGENT.md."""
        frontmatter_pattern = re.compile(r"^\s*---\s*\n(.*?)\n\s*---\s*\n?(.*)$", re.DOTALL)
        match = frontmatter_pattern.match(content)

        if match:
            yaml_str, body = match.group(1), match.group(2)
            try:
                data = yaml.safe_load(yaml_str) or {}
                return data, body.strip()
            except Exception as e:
                raise ValueError(f"Invalid YAML frontmatter in AGENT.md: {e}") from e

        return {}, content.strip()

    def load_agent_file(self, file_path: str | Path) -> AgentDefinition:
        """Load an AgentDefinition from an AGENT.md or YAML file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Agent charter file not found: {file_path}")

        content = path.read_text(encoding="utf-8")

        if path.name.endswith(".md") or path.name.lower() == "agent.md":
            data, body = self.parse_frontmatter_markdown(content)
        else:
            data = yaml.safe_load(content) or {}
            body = data.get("system_prompt", "")

        agent_id = str(data.get("id") or data.get("name") or path.stem).lower().replace(" ", "_")
        name = str(data.get("name") or path.stem.capitalize())
        role = str(data.get("role") or "assistant")
        description = str(data.get("description") or "")
        system_prompt = str(data.get("system_prompt") or body)
        required_skills = list(data.get("required_skills") or data.get("skills") or [])

        # Parse permissions
        perm_data = data.get("permissions") or {}
        if isinstance(perm_data, dict):
            access_levels_raw = perm_data.get("access_levels", ["read_only"])
            access_levels = [ToolAccessLevel(lvl) for lvl in access_levels_raw if lvl in ToolAccessLevel._value2member_map_]
            permissions = PermissionPolicy(
                access_levels=access_levels or [ToolAccessLevel.READ_ONLY],
                allowed_tools=list(perm_data.get("allowed_tools", [])),
                denied_tools=list(perm_data.get("denied_tools", [])),
                allowed_paths=list(perm_data.get("allowed_paths", [])),
                max_execution_time_sec=float(perm_data.get("max_execution_time_sec", 60.0)),
                rate_limit_per_min=int(perm_data.get("rate_limit_per_min", 60)),
            )
        else:
            permissions = PermissionPolicy()

        return AgentDefinition(
            id=agent_id,
            name=name,
            role=role,
            description=description,
            system_prompt=system_prompt,
            required_skills=required_skills,
            permissions=permissions,
            model_preference=data.get("model_preference"),
            metadata=data.get("metadata", {}),
        )

    def instantiate_agent(self, definition: AgentDefinition) -> ConfiguredAgent:
        """Create a runnable ConfiguredAgent instance from an AgentDefinition."""
        return ConfiguredAgent(definition)

    def scan_directory(self, dir_path: str | Path) -> List[AgentDefinition]:
        """Recursively scan directory for AGENT.md and agent.yaml files."""
        root = Path(dir_path)
        if not root.exists() or not root.is_dir():
            return []

        loaded: List[AgentDefinition] = []
        for path in root.rglob("*"):
            if path.is_file() and path.name.lower() in ("agent.md", "agent.yaml", "agent.yml"):
                try:
                    agent_def = self.load_agent_file(path)
                    loaded.append(agent_def)
                except Exception:
                    continue

        return loaded

"""Abstract Agent interface for AI-Agent-OS.

Agents are the "Who" — they represent roles, workflows, and handoff rules.
Skills are the "What" — they provide capabilities that agents load dynamically.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.core.task import Task
from src.core.event import Event, EventBus
from src.core.state import AgentStateInfo
from src.schemas.common import AgentCapability, AgentState


class BaseAgent(ABC):
    """Abstract base class for all agents in AI-Agent-OS.

    An agent is defined by:
    - id: Unique identifier
    - name: Human-readable name
    - description: What this agent does
    - capabilities: What the agent can do (declared)
    - loaded_skills: Skills dynamically loaded at runtime
    - state: Current lifecycle state

    Agents MUST NOT have hardcoded capabilities.
    Skills MUST be loaded dynamically.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str = "",
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._id = agent_id
        self._name = name
        self._description = description
        self._capabilities: List[AgentCapability] = []
        self._loaded_skills: Dict[str, Any] = {}
        self._state: AgentState = AgentState.IDLE
        self._event_bus = event_bus or EventBus()
        self._metadata: Dict[str, Any] = {}

    # ── Properties ──────────────────────────────────────────

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def capabilities(self) -> List[AgentCapability]:
        return list(self._capabilities)

    @property
    def loaded_skills(self) -> Dict[str, Any]:
        return dict(self._loaded_skills)

    @property
    def state(self) -> AgentState:
        return self._state

    # ── Lifecycle Methods ───────────────────────────────────

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent.

        Called once when the agent is first created.
        Should load default skills and set up resources.
        """
        ...

    @abstractmethod
    async def execute(self, task: Task) -> Task:
        """Execute a given task.

        This is the main entry point for doing work.
        The agent processes the task input and returns the completed/failed task.
        """
        ...

    async def on_start(self) -> None:
        """Hook called before the agent starts executing its first task."""
        pass

    @abstractmethod
    async def pause(self) -> None:
        """Pause the agent's execution.

        The agent should save its current state and stop processing.
        """
        ...

    async def on_pause(self) -> None:
        """Hook called when the agent is paused."""
        pass

    @abstractmethod
    async def resume(self) -> None:
        """Resume the agent from a paused state.

        The agent should restore its state and continue processing.
        """
        ...

    async def on_resume(self) -> None:
        """Hook called when the agent is resumed."""
        pass

    @abstractmethod
    async def terminate(self) -> None:
        """Terminate the agent.

        Clean up all resources, unload skills, and mark as terminated.
        """
        ...

    async def on_terminate(self) -> None:
        """Hook called when the agent is terminated."""
        pass

    # ── Task Management ─────────────────────────────────────
    
    def get_active_tasks(self) -> List[Task]:
        """Return the list of tasks currently being processed."""
        # By default this is managed by the subclass implementation of execute()
        # but we provide a default empty implementation if not overridden.
        return []

    # ── Skill Management ────────────────────────────────────

    def add_capability(self, capability: AgentCapability) -> None:
        """Declare a capability for this agent."""
        self._capabilities.append(capability)

    def load_skill(self, skill_name: str, skill_instance: Any) -> None:
        """Dynamically load a skill into the agent.

        Skills are loaded at runtime, not hardcoded.
        """
        self._loaded_skills[skill_name] = skill_instance

    def unload_skill(self, skill_name: str) -> None:
        """Remove a dynamically loaded skill."""
        self._loaded_skills.pop(skill_name, None)

    def has_skill(self, skill_name: str) -> bool:
        """Check if a skill is loaded."""
        return skill_name in self._loaded_skills

    # ── Event Handling ──────────────────────────────────────

    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit a system event."""
        from src.schemas.common import EventType

        event = Event(
            type=EventType(event_type),
            source=self._id,
            data=data,
        )
        await self._event_bus.publish(event)

    # ── State Management ────────────────────────────────────

    def _set_state(self, new_state: AgentState) -> None:
        """Update the agent's internal state."""
        self._state = new_state
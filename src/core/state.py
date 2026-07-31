"""Agent state management for AI-Agent-OS."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Set

from pydantic import BaseModel, Field

from src.schemas.common import AgentState


class AgentStateInfo(BaseModel):
    """Captures the full state snapshot of an agent."""

    agent_id: str
    state: AgentState = AgentState.IDLE
    current_task_id: Optional[str] = None
    loaded_skills: Dict[str, str] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StateManager:
    """Manages state transitions for agents.

    Ensures that only valid state transitions are allowed,
    guarding against illegal state changes.
    """

    VALID_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
        AgentState.IDLE: {AgentState.INITIALIZING, AgentState.RUNNING, AgentState.TERMINATED},
        AgentState.INITIALIZING: {AgentState.IDLE, AgentState.RUNNING, AgentState.TERMINATED},
        AgentState.RUNNING: {AgentState.PAUSED, AgentState.TERMINATED, AgentState.IDLE},
        AgentState.PAUSED: {AgentState.RUNNING, AgentState.TERMINATED},
        AgentState.TERMINATED: set(),
    }

    def __init__(self) -> None:
        self._agents: Dict[str, AgentStateInfo] = {}

    def register(self, agent_id: str) -> AgentStateInfo:
        """Register a new agent with IDLE state."""
        info = AgentStateInfo(agent_id=agent_id)
        self._agents[agent_id] = info
        return info

    def unregister(self, agent_id: str) -> None:
        """Remove an agent from state tracking."""
        self._agents.pop(agent_id, None)

    def transition_to(
        self,
        agent_id: str,
        new_state: AgentState,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentStateInfo:
        """Transition an agent to a new state with validation."""
        info = self._agents.get(agent_id)
        if info is None:
            raise ValueError(f"Agent '{agent_id}' is not registered")

        current = info.state
        allowed = self.VALID_TRANSITIONS.get(current, set())
        if new_state not in allowed:
            raise ValueError(
                f"Invalid state transition for agent '{agent_id}': "
                f"{current.value} -> {new_state.value}"
            )

        # Update timestamps on specific transitions
        if new_state == AgentState.RUNNING and current == AgentState.IDLE:
            info.started_at = datetime.utcnow()
        if new_state == AgentState.PAUSED:
            info.paused_at = datetime.utcnow()

        info.state = new_state
        if metadata:
            info.metadata.update(metadata)

        return info

    def get_state(self, agent_id: str) -> AgentStateInfo:
        """Get the current state info for an agent."""
        info = self._agents.get(agent_id)
        if info is None:
            raise ValueError(f"Agent '{agent_id}' is not registered")
        return info

    def list_states(self) -> Dict[str, AgentStateInfo]:
        """Return all tracked agent states."""
        return dict(self._agents)

    def update_metadata(self, agent_id: str, metadata: Dict[str, Any]) -> None:
        """Update the metadata for an agent's state."""
        info = self._agents.get(agent_id)
        if info:
            info.metadata.update(metadata)
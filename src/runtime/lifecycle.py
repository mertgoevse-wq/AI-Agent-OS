"""Lifecycle management for AI-Agent-OS.

Orchestrates the lifecycle of agents: initialize → run → pause → resume → terminate.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.agent import BaseAgent
from src.core.event import Event, EventBus
from src.core.state import StateManager
from src.schemas.common import AgentState, EventType


class LifecycleManager:
    """Manages the lifecycle of all agents in the system.

    Provides a clean API for starting, stopping, pausing, and resuming agents.
    Emits lifecycle events to the EventBus for observability.
    """

    def __init__(
        self,
        state_manager: StateManager,
        event_bus: EventBus,
    ) -> None:
        self._state_manager = state_manager
        self._event_bus = event_bus

    async def initialize_agent(self, agent: BaseAgent) -> None:
        """Initialize an agent and transition it to IDLE state.

        Args:
            agent: The agent to initialize.

        Raises:
            ValueError: If the agent is already registered.
        """
        self._state_manager.register(agent.id)
        await agent.initialize()

        await self._event_bus.publish(
            Event(
                type=EventType.AGENT_STARTED,
                source="lifecycle_manager",
                data={"agent_id": agent.id, "name": agent.name},
            )
        )

    async def start_agent(self, agent: BaseAgent) -> None:
        """Start an agent, transitioning it to RUNNING state.

        Args:
            agent: The agent to start.

        Raises:
            ValueError: If the state transition is invalid.
        """
        self._state_manager.transition_to(agent.id, AgentState.RUNNING)

        await self._event_bus.publish(
            Event(
                type=EventType.AGENT_STARTED,
                source="lifecycle_manager",
                data={"agent_id": agent.id, "state": AgentState.RUNNING.value},
            )
        )

    async def pause_agent(self, agent: BaseAgent) -> None:
        """Pause an agent, transitioning it to PAUSED state.

        Args:
            agent: The agent to pause.
        """
        await agent.pause()
        self._state_manager.transition_to(agent.id, AgentState.PAUSED)

        await self._event_bus.publish(
            Event(
                type=EventType.AGENT_PAUSED,
                source="lifecycle_manager",
                data={"agent_id": agent.id},
            )
        )

    async def resume_agent(self, agent: BaseAgent) -> None:
        """Resume a paused agent, transitioning it to RUNNING state.

        Args:
            agent: The agent to resume.
        """
        await agent.resume()
        self._state_manager.transition_to(agent.id, AgentState.RUNNING)

        await self._event_bus.publish(
            Event(
                type=EventType.AGENT_RESUMED,
                source="lifecycle_manager",
                data={"agent_id": agent.id},
            )
        )

    async def terminate_agent(self, agent: BaseAgent) -> None:
        """Terminate an agent, cleaning up all resources.

        Args:
            agent: The agent to terminate.
        """
        await agent.terminate()
        self._state_manager.transition_to(agent.id, AgentState.TERMINATED)

        await self._event_bus.publish(
            Event(
                type=EventType.AGENT_STOPPED,
                source="lifecycle_manager",
                data={"agent_id": agent.id},
            )
        )

    def get_agent_state(self, agent_id: str) -> AgentState:
        """Get the current state of an agent.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            The current AgentState.
        """
        info = self._state_manager.get_state(agent_id)
        return info.state

    def list_agent_states(self) -> Dict[str, AgentState]:
        """List all agents and their current states.

        Returns:
            A dict mapping agent IDs to their current states.
        """
        states = self._state_manager.list_states()
        return {aid: info.state for aid, info in states.items()}
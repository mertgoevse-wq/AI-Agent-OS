"""Tests for the State Manager."""

import pytest
from src.core.state import StateManager, AgentStateInfo
from src.schemas.common import AgentState


class TestStateManager:
    """Test agent state management."""

    def test_register_agent(self):
        manager = StateManager(":memory:")
        info = manager.register("agent-1")
        assert info.agent_id == "agent-1"
        assert info.state == AgentState.IDLE

    def test_register_duplicate(self):
        manager = StateManager(":memory:")
        manager.register("agent-1")
        # Registering again should overwrite (no error)
        info = manager.register("agent-1")
        assert info.agent_id == "agent-1"

    def test_unregister_agent(self):
        manager = StateManager(":memory:")
        manager.register("agent-1")
        manager.unregister("agent-1")
        with pytest.raises(ValueError, match="not registered"):
            manager.get_state("agent-1")

    def test_get_state(self):
        manager = StateManager(":memory:")
        manager.register("agent-1")
        info = manager.get_state("agent-1")
        assert info.agent_id == "agent-1"

    def test_get_state_unregistered(self):
        manager = StateManager(":memory:")
        with pytest.raises(ValueError, match="not registered"):
            manager.get_state("unknown")

    def test_list_states(self):
        manager = StateManager(":memory:")
        manager.register("agent-1")
        manager.register("agent-2")
        states = manager.list_states()
        assert len(states) == 2
        assert "agent-1" in states
        assert "agent-2" in states


class TestStateTransitions:
    """Test valid and invalid state transitions."""

    def setup_method(self):
        self.manager = StateManager(":memory:")
        self.manager.register("agent-1")

    def test_idle_to_initializing(self):
        self.manager.transition_to("agent-1", AgentState.INITIALIZING)
        assert self.manager.get_state("agent-1").state == AgentState.INITIALIZING

    def test_idle_to_terminated(self):
        self.manager.transition_to("agent-1", AgentState.TERMINATED)
        assert self.manager.get_state("agent-1").state == AgentState.TERMINATED

    def test_initializing_to_running(self):
        self.manager.transition_to("agent-1", AgentState.INITIALIZING)
        self.manager.transition_to("agent-1", AgentState.RUNNING)
        assert self.manager.get_state("agent-1").state == AgentState.RUNNING

    def test_running_to_paused(self):
        self.manager.transition_to("agent-1", AgentState.INITIALIZING)
        self.manager.transition_to("agent-1", AgentState.RUNNING)
        self.manager.transition_to("agent-1", AgentState.PAUSED)
        assert self.manager.get_state("agent-1").state == AgentState.PAUSED

    def test_paused_to_running(self):
        self.manager.transition_to("agent-1", AgentState.INITIALIZING)
        self.manager.transition_to("agent-1", AgentState.RUNNING)
        self.manager.transition_to("agent-1", AgentState.PAUSED)
        self.manager.transition_to("agent-1", AgentState.RUNNING)
        assert self.manager.get_state("agent-1").state == AgentState.RUNNING

    def test_running_to_terminated(self):
        self.manager.transition_to("agent-1", AgentState.INITIALIZING)
        self.manager.transition_to("agent-1", AgentState.RUNNING)
        self.manager.transition_to("agent-1", AgentState.TERMINATED)
        assert self.manager.get_state("agent-1").state == AgentState.TERMINATED

    def test_invalid_transition_raises(self):
        self.manager.transition_to("agent-1", AgentState.INITIALIZING)
        self.manager.transition_to("agent-1", AgentState.RUNNING)
        self.manager.transition_to("agent-1", AgentState.TERMINATED)
        # Terminated -> anything is invalid
        with pytest.raises(ValueError, match="Invalid state transition"):
            self.manager.transition_to("agent-1", AgentState.RUNNING)

    def test_idle_to_running_valid(self):
        self.manager.transition_to("agent-1", AgentState.RUNNING)
        assert self.manager.get_state("agent-1").state == AgentState.RUNNING

    def test_transition_with_metadata(self):
        self.manager.transition_to(
            "agent-1",
            AgentState.INITIALIZING,
            metadata={"reason": "boot"},
        )
        info = self.manager.get_state("agent-1")
        assert info.metadata.get("reason") == "boot"

    def test_update_metadata(self):
        self.manager.update_metadata("agent-1", {"key": "value"})
        info = self.manager.get_state("agent-1")
        assert info.metadata.get("key") == "value"
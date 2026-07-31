"""Tests for the Agent Registry."""

import pytest
from src.registry.agent_registry import AgentRegistry

from src.core.agent import BaseAgent
from src.core.task import Task


class SimpleAgent(BaseAgent):
    async def initialize(self) -> None: pass
    async def execute(self, task: Task) -> Task: return task
    async def pause(self) -> None: pass
    async def resume(self) -> None: pass
    async def terminate(self) -> None: pass


class TestAgentRegistry:
    """Test the Agent Registry."""

    def setup_method(self):
        self.registry = AgentRegistry()
        self.agent = SimpleAgent(agent_id="agent-1", name="Test Agent")

    def test_register_agent(self):
        self.registry.register_agent(self.agent)
        assert self.registry.count() == 1

    def test_register_duplicate_raises(self):
        self.registry.register_agent(self.agent)
        with pytest.raises(ValueError, match="already registered"):
            self.registry.register_agent(self.agent)

    def test_get_agent(self):
        self.registry.register_agent(self.agent)
        retrieved = self.registry.get_agent("agent-1")
        assert retrieved is not None
        assert retrieved.id == "agent-1"
        assert retrieved.name == "Test Agent"

    def test_get_agent_not_found(self):
        assert self.registry.get_agent("nonexistent") is None

    def test_list_agents(self):
        agent2 = SimpleAgent(agent_id="agent-2", name="Agent 2")
        self.registry.register_agent(self.agent)
        self.registry.register_agent(agent2)
        agents = self.registry.list_agents()
        assert len(agents) == 2

    def test_unregister_agent(self):
        self.registry.register_agent(self.agent)
        self.registry.unregister_agent("agent-1")
        assert self.registry.count() == 0

    def test_has_agent(self):
        self.registry.register_agent(self.agent)
        assert self.registry.has_agent("agent-1") is True
        assert self.registry.has_agent("nonexistent") is False

    def test_count(self):
        assert self.registry.count() == 0
        self.registry.register_agent(self.agent)
        assert self.registry.count() == 1
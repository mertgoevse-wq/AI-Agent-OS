"""Tests for the Agent lifecycle."""

import pytest
from src.core.agent import BaseAgent
from src.core.task import Task
from src.core.event import EventBus
from src.schemas.common import AgentCapability, AgentState, TaskStatus


class SimpleAgent(BaseAgent):
    """A simple concrete agent for testing."""

    async def initialize(self) -> None:
        self._initialized = True

    async def execute(self, task: Task) -> Task:
        task.complete(f"Executed: {task.input}")
        return task

    async def pause(self) -> None:
        self._paused = True

    async def resume(self) -> None:
        self._resumed = True

    async def terminate(self) -> None:
        self._terminated = True


class TestAgentCreation:
    """Test agent creation and properties."""

    def test_agent_creates_with_defaults(self):
        agent = SimpleAgent(agent_id="agent-1", name="Test Agent")
        assert agent.id == "agent-1"
        assert agent.name == "Test Agent"
        assert agent.description == ""
        assert agent.state == AgentState.IDLE
        assert agent.capabilities == []
        assert agent.loaded_skills == {}

    def test_agent_with_description(self):
        agent = SimpleAgent(
            agent_id="agent-2",
            name="Research Agent",
            description="Performs research tasks",
        )
        assert agent.description == "Performs research tasks"

    def test_agent_with_event_bus(self):
        bus = EventBus()
        agent = SimpleAgent(agent_id="agent-3", name="Bus Agent", event_bus=bus)
        assert agent._event_bus is bus


class TestAgentCapabilities:
    """Test capability management."""

    def test_add_capability(self):
        agent = SimpleAgent(agent_id="a1", name="Agent")
        cap = AgentCapability(name="research", description="Can research")
        agent.add_capability(cap)
        assert len(agent.capabilities) == 1
        assert agent.capabilities[0].name == "research"

    def test_agent_has_no_hardcoded_capabilities(self):
        """Agents must not have hardcoded capabilities."""
        agent = SimpleAgent(agent_id="a1", name="Agent")
        assert agent.capabilities == []


class TestAgentSkills:
    """Test dynamic skill loading."""

    def test_load_skill(self):
        agent = SimpleAgent(agent_id="a1", name="Agent")
        skill = {"name": "web_search"}
        agent.load_skill("web_search", skill)
        assert agent.has_skill("web_search")
        assert agent.loaded_skills["web_search"] == skill

    def test_unload_skill(self):
        agent = SimpleAgent(agent_id="a1", name="Agent")
        agent.load_skill("web_search", {})
        agent.unload_skill("web_search")
        assert not agent.has_skill("web_search")

    def test_agent_has_no_hardcoded_skills(self):
        """Agents must not have hardcoded skills."""
        agent = SimpleAgent(agent_id="a1", name="Agent")
        assert agent.loaded_skills == {}


class TestAgentLifecycle:
    """Test the agent lifecycle methods."""

    @pytest.mark.asyncio
    async def test_initialize(self):
        agent = SimpleAgent(agent_id="a1", name="Agent")
        assert not hasattr(agent, '_initialized')
        await agent.initialize()
        assert agent._initialized is True

    @pytest.mark.asyncio
    async def test_execute(self):
        agent = SimpleAgent(agent_id="a1", name="Agent")
        task = Task(input="hello")
        task.transition_to(TaskStatus.RUNNING)
        result = await agent.execute(task)
        assert result.status.value == "completed"
        assert result.result == "Executed: hello"

    @pytest.mark.asyncio
    async def test_pause_and_resume(self):
        agent = SimpleAgent(agent_id="a1", name="Agent")
        await agent.pause()
        assert agent._paused is True
        await agent.resume()
        assert agent._resumed is True

    @pytest.mark.asyncio
    async def test_terminate(self):
        agent = SimpleAgent(agent_id="a1", name="Agent")
        await agent.terminate()
        assert agent._terminated is True
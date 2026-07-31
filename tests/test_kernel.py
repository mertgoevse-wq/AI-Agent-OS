"""Integration tests for the Kernel."""

import pytest
from src.runtime.kernel import Kernel
from src.core.agent import BaseAgent
from src.core.task import Task
from src.schemas.common import TaskStatus, EventType


class TestAgent(BaseAgent):
    """A test agent that processes tasks with a simple echo."""

    async def initialize(self) -> None:
        self._initialized = True

    async def execute(self, task: Task) -> Task:
        task.complete(f"Processed: {task.input}")
        return task

    async def pause(self) -> None:
        self._paused = True

    async def resume(self) -> None:
        self._resumed = True

    async def terminate(self) -> None:
        self._terminated = True


class FailingAgent(BaseAgent):
    """An agent that fails during task execution."""

    async def initialize(self) -> None:
        pass

    async def execute(self, task: Task) -> Task:
        raise RuntimeError("Task execution failed")

    async def pause(self) -> None:
        pass

    async def resume(self) -> None:
        pass

    async def terminate(self) -> None:
        pass


class TestKernel:
    """Integration tests for the Kernel."""

    @pytest.mark.asyncio
    async def test_kernel_boot_and_shutdown(self):
        kernel = Kernel(state_db_path=":memory:")
        assert kernel.is_running is False
        await kernel.boot()
        assert kernel.is_running is True
        await kernel.shutdown()
        assert kernel.is_running is False

    @pytest.mark.asyncio
    async def test_register_agent(self):
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()
        agent = TestAgent(agent_id="agent-1", name="Test Agent")
        await kernel.register_agent(agent)

        assert kernel.get_agent("agent-1") is not None
        assert len(kernel.list_agents()) == 1
        assert kernel.get_agent_state("agent-1") == "idle"

        await kernel.shutdown()

    @pytest.mark.asyncio
    async def test_register_duplicate_agent(self):
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()
        agent = TestAgent(agent_id="agent-1", name="Test")
        await kernel.register_agent(agent)
        with pytest.raises(ValueError, match="already registered"):
            await kernel.register_agent(agent)
        await kernel.shutdown()

    @pytest.mark.asyncio
    async def test_agent_lifecycle(self):
        """Test full agent lifecycle: register -> start -> pause -> resume -> stop."""
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()
        agent = TestAgent(agent_id="agent-1", name="Lifecycle Agent")
        await kernel.register_agent(agent)

        assert kernel.get_agent_state("agent-1") == "idle"

        await kernel.start_agent("agent-1")
        assert kernel.get_agent_state("agent-1") == "running"

        await kernel.pause_agent("agent-1")
        assert kernel.get_agent_state("agent-1") == "paused"

        await kernel.resume_agent("agent-1")
        assert kernel.get_agent_state("agent-1") == "running"

        await kernel.unregister_agent("agent-1")
        assert kernel.get_agent("agent-1") is None

        await kernel.shutdown()

    @pytest.mark.asyncio
    async def test_submit_task(self):
        """Test submitting a task to the kernel."""
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()
        agent = TestAgent(agent_id="agent-1", name="Worker")
        await kernel.register_agent(agent)
        await kernel.start_agent("agent-1")

        task = Task(input="test task")
        result = await kernel.submit_task(task)
        
        import asyncio
        for _ in range(20):
            if result.status != TaskStatus.PENDING and result.status != TaskStatus.RUNNING:
                break
            await asyncio.sleep(0.05)

        assert result.status == TaskStatus.COMPLETED
        assert result.result == "Processed: test task"
        assert result.agent_id == "agent-1"

        await kernel.shutdown()

    @pytest.mark.asyncio
    async def test_submit_task_no_agent(self):
        """Task should fail if no agent is available."""
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()

        task = Task(input="orphan task")
        result = await kernel.submit_task(task)

        import asyncio
        for _ in range(20):
            if result.status != TaskStatus.PENDING and result.status != TaskStatus.RUNNING:
                break
            await asyncio.sleep(0.05)

        assert result.status == TaskStatus.FAILED
        assert "No available agent" in result.error

        await kernel.shutdown()

    @pytest.mark.asyncio
    async def test_submit_task_to_specific_agent(self):
        """Task should be executed by the specified agent."""
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()
        agent = TestAgent(agent_id="agent-1", name="Worker")
        await kernel.register_agent(agent)
        await kernel.start_agent("agent-1")

        task = Task(input="specific task", agent_id="agent-1")
        result = await kernel.submit_task(task)

        import asyncio
        for _ in range(20):
            if result.status != TaskStatus.PENDING and result.status != TaskStatus.RUNNING:
                break
            await asyncio.sleep(0.05)

        assert result.status == TaskStatus.COMPLETED
        assert result.agent_id == "agent-1"

        await kernel.shutdown()

    @pytest.mark.asyncio
    async def test_task_failure(self):
        """Task should be marked as failed when agent raises exception."""
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()
        agent = FailingAgent(agent_id="agent-fail", name="Failing Agent")
        await kernel.register_agent(agent)
        await kernel.start_agent("agent-fail")

        task = Task(input="will fail")
        result = await kernel.submit_task(task)

        import asyncio
        for _ in range(20):
            if result.status != TaskStatus.PENDING and result.status != TaskStatus.RUNNING:
                break
            await asyncio.sleep(0.05)

        assert result.status == TaskStatus.FAILED
        assert result.error is not None

        await kernel.shutdown()

    @pytest.mark.asyncio
    async def test_kernel_emits_events(self):
        """Kernel should emit events during lifecycle."""
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()

        events = []
        async def collect_events(event):
            events.append(event.type)

        kernel.event_bus.subscribe(EventType.AGENT_STARTED, collect_events)
        kernel.event_bus.subscribe(EventType.AGENT_STOPPED, collect_events)

        agent = TestAgent(agent_id="agent-1", name="Test")
        await kernel.register_agent(agent)
        await kernel.shutdown()

        assert EventType.AGENT_STARTED in events
        assert EventType.AGENT_STOPPED in events

    @pytest.mark.asyncio
    async def test_multiple_agents(self):
        """Kernel should support multiple agents."""
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()

        agent1 = TestAgent(agent_id="agent-1", name="Agent 1")
        agent2 = TestAgent(agent_id="agent-2", name="Agent 2")
        await kernel.register_agent(agent1)
        await kernel.register_agent(agent2)

        assert len(kernel.list_agents()) == 2

        await kernel.shutdown()

    @pytest.mark.asyncio
    async def test_start_nonexistent_agent(self):
        """Starting a non-existent agent should raise."""
        kernel = Kernel(state_db_path=":memory:")
        await kernel.boot()
        with pytest.raises(ValueError, match="not found"):
            await kernel.start_agent("nonexistent")
        await kernel.shutdown()
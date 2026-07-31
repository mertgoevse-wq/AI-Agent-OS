"""Core Kernel for AI-Agent-OS.

The Kernel is the central orchestrator that ties together:
- Agent lifecycle management
- Event bus communication
- Task distribution
- Skill and agent registries
- Model routing
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from src.core.agent import BaseAgent
from src.core.event import Event, EventBus
from src.core.state import StateManager
from src.core.task import Task
from src.models.router import ModelRouter
from src.models.providers import MockProvider
from src.registry.agent_registry import AgentRegistry
from src.registry.skill_registry import SkillRegistry
from src.runtime.lifecycle import LifecycleManager
from src.schemas.common import EventType, TaskStatus


class Kernel:
    """Central kernel of the AI-Agent-OS.

    Coordinates all system components and provides the main API
    for interacting with the agent runtime.
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        agent_registry: Optional[AgentRegistry] = None,
        skill_registry: Optional[SkillRegistry] = None,
        model_router: Optional[ModelRouter] = None,
        state_db_path: str = "state.db",
    ) -> None:
        # Core infrastructure
        self.event_bus = event_bus or EventBus()
        self.state_manager = StateManager(db_path=state_db_path)
        self.lifecycle = LifecycleManager(
            state_manager=self.state_manager,
            event_bus=self.event_bus,
        )

        # Registries
        self.agent_registry = agent_registry or AgentRegistry()
        self.skill_registry = skill_registry or SkillRegistry()
        from src.registry.plugin_registry import PluginRegistry
        self.plugin_registry = PluginRegistry()

        # Model routing
        self.model_router = model_router or ModelRouter()
        if not self.model_router.list_providers():
            self._setup_default_providers()

        # Runtime state
        self._running = False
        from src.runtime.queue import InMemoryTaskQueue
        self.task_queue = InMemoryTaskQueue()
        self._worker_task: Optional[asyncio.Task] = None

    def _setup_default_providers(self) -> None:
        """Register the default mock provider."""
        self.model_router.register_provider("mock", MockProvider())

    async def boot(self) -> None:
        """Boot the kernel."""
        self._running = True
        self._worker_task = asyncio.create_task(self._task_worker())
        await self.event_bus.publish(
            Event(
                type=EventType.AGENT_STARTED,
                source="kernel",
                data={"message": "Kernel boot sequence complete"},
            )
        )

    async def _task_worker(self) -> None:
        """Background worker that pulls tasks from the queue and executes them."""
        import asyncio
        while self._running:
            try:
                task = await asyncio.wait_for(self.task_queue.dequeue(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            
            try:
                await self._execute_task(task)
            except Exception as e:
                task.fail(str(e))
                await self._publish_task_failed(task)
            finally:
                if hasattr(self.task_queue, 'task_done'):
                    self.task_queue.task_done()

    async def shutdown(self) -> None:
        """Shut down the kernel."""
        self._running = False
        
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        # Terminate all agents
        for agent in self.agent_registry.list_agents():
            try:
                await self.lifecycle.terminate_agent(agent)
            except Exception:
                pass

        await self.event_bus.publish(
            Event(
                type=EventType.AGENT_STOPPED,
                source="kernel",
                data={"message": "Kernel shutdown complete"},
            )
        )

    async def load_plugin(self, manifest_path: str) -> None:
        """Load and initialize a plugin from a manifest path."""
        definition = self.plugin_registry.loader.load_plugin_manifest(manifest_path)
        plugin_class = self.plugin_registry.loader.load_plugin_class(definition)
        plugin_instance = plugin_class(
            event_bus=self.event_bus,
            agent_registry=self.agent_registry,
            skill_registry=self.skill_registry,
            config=definition.config,
        )
        self.plugin_registry.register(plugin_instance, definition)
        await plugin_instance.initialize()

    async def register_agent(self, agent: BaseAgent) -> None:
        """Register and initialize a new agent."""
        self.agent_registry.register_agent(agent)
        await self.lifecycle.initialize_agent(agent)

    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister and terminate an agent."""
        agent = self.agent_registry.get_agent(agent_id)
        if agent:
            await self.lifecycle.terminate_agent(agent)
            self.agent_registry.unregister_agent(agent_id)

    async def start_agent(self, agent_id: str) -> None:
        """Start a registered agent."""
        agent = self.agent_registry.get_agent(agent_id)
        if agent is None:
            raise ValueError(f"Agent '{agent_id}' not found")
        await self.lifecycle.start_agent(agent)

    async def pause_agent(self, agent_id: str) -> None:
        """Pause a running agent."""
        agent = self.agent_registry.get_agent(agent_id)
        if agent:
            await self.lifecycle.pause_agent(agent)

    async def resume_agent(self, agent_id: str) -> None:
        """Resume a paused agent."""
        agent = self.agent_registry.get_agent(agent_id)
        if agent:
            await self.lifecycle.resume_agent(agent)

    async def submit_task(self, task: Task) -> Task:
        """Submit a task for asynchronous execution via the queue."""
        await self.event_bus.publish(
            Event(
                type=EventType.TASK_CREATED,
                source="kernel",
                data={"task_id": task.id, "type": task.type},
            )
        )
        
        await self.task_queue.enqueue(task, priority=10)
        return task
        
    async def _execute_task(self, task: Task) -> Task:
        """Synchronously execute a task (called by the worker)."""
        # Find an agent to execute the task
        if task.agent_id:
            agent = self.agent_registry.get_agent(task.agent_id)
        else:
            # Pick the first available agent
            agents = self.agent_registry.list_agents()
            agent = agents[0] if agents else None

        if agent is None:
            task.fail("No available agent to execute task")
            await self._publish_task_failed(task)
            return task

        task.assign_to(agent.id)
        task.transition_to(TaskStatus.RUNNING)

        try:
            result = await agent.execute(task)
            await self.event_bus.publish(
                Event(
                    type=EventType.TASK_COMPLETED,
                    source="kernel",
                    data={"task_id": task.id, "agent_id": agent.id},
                )
            )
            return result
        except Exception as e:
            task.fail(str(e))
            await self._publish_task_failed(task)
            return task

    async def _publish_task_failed(self, task: Task) -> None:
        """Publish a task failed event."""
        await self.event_bus.publish(
            Event(
                type=EventType.TASK_FAILED,
                source="kernel",
                data={
                    "task_id": task.id,
                    "agent_id": task.agent_id,
                    "error": task.error,
                },
            )
        )

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get a registered agent by ID."""
        return self.agent_registry.get_agent(agent_id)

    def list_agents(self) -> List[BaseAgent]:
        """List all registered agents."""
        return self.agent_registry.list_agents()

    def get_agent_state(self, agent_id: str) -> str:
        """Get the current state of an agent."""
        return self.lifecycle.get_agent_state(agent_id).value

    @property
    def is_running(self) -> bool:
        """Check if the kernel is running."""
        return self._running
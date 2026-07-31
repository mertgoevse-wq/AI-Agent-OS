"""Agent Execution Engine

Manages the runtime context and execution of tasks by agents. 
Responsible for providing agents with secure access to Memory, Skills, Tools, and the Model Router.
"""

import logging
from typing import Optional, Dict, Any, List

from src.core.agent import BaseAgent
from src.core.task import Task
from src.schemas.common import TaskStatus, AgentState
from src.router.model_router import ModelRouter
from src.registry.skill_registry import SkillRegistry
from src.memory.memory_system import MemorySystem

logger = logging.getLogger(__name__)

class AgentExecutionContext:
    """Isolated context provided to an agent during task execution."""
    
    def __init__(
        self,
        agent: BaseAgent,
        task: Task,
        model_router: ModelRouter,
        skill_registry: SkillRegistry,
        memory_system: Optional[MemorySystem] = None
    ) -> None:
        self.agent = agent
        self.task = task
        self.model_router = model_router
        self.skill_registry = skill_registry
        self.memory_system = memory_system
        self.execution_metadata: Dict[str, Any] = {}

    def get_memory_context(self, query: str) -> List[Any]:
        """Fetch relevant knowledge from Vector and STM."""
        if self.memory_system:
            # Stub for real vector retrieval
            return []
        return []
        
    def get_available_skills(self) -> List[str]:
        """Get skills bound to the current agent context."""
        return list(self.skill_registry.list_skills().keys())

    async def execute_model(self, prompt: str, **kwargs) -> Any:
        """Route model requests through the central router."""
        return await self.model_router.route(prompt, **kwargs)


class AgentExecutionEngine:
    """Manages the lifecycle and isolated execution of agent tasks."""

    def __init__(
        self,
        model_router: ModelRouter,
        skill_registry: SkillRegistry,
        memory_system: Optional[MemorySystem] = None
    ):
        self.model_router = model_router
        self.skill_registry = skill_registry
        self.memory_system = memory_system

    async def execute_task(self, agent: BaseAgent, task: Task) -> Task:
        """Execute a task in an isolated context and handle state transitions."""
        logger.info(f"Engine starting execution for task {task.task_id} by agent {agent.agent_id}")
        
        context = AgentExecutionContext(
            agent=agent,
            task=task,
            model_router=self.model_router,
            skill_registry=self.skill_registry,
            memory_system=self.memory_system
        )
        
        try:
            task.status = TaskStatus.RUNNING
            # Execute agent logic with provided context (In a real scenario, we'd pass context to execute)
            # Since BaseAgent expects just `task`, we assume it pulls context if needed, or we enhance it later.
            result_task = await agent.execute(task)
            result_task.status = TaskStatus.COMPLETED
            return result_task
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            task.fail(str(e))
            return task

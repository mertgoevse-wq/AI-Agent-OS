import pytest
import asyncio
from src.runtime.agent_runtime import AgentRuntimeEngine
from src.core.task_router import TaskRouter
from src.runtime.skill_executor import SkillExecutionLayer, SkillExecutionError
from src.memory.memory_manager import MemoryManager
from src.core.model_router import ModelRouter
from src.runtime.worker import WorkerSystem
from src.registry.prompt_registry import PromptRegistry

class MockSkillRegistry:
    def has_skill(self, name):
        return name in ["code_analysis", "mcp_connector"]
    def get_skill(self, name):
        return f"mock_{name}_instance"

class MockAgentRegistry:
    pass

@pytest.fixture
def execution_engine_deps():
    return {
        "agent_registry": MockAgentRegistry(),
        "skill_registry": MockSkillRegistry(),
        "prompt_registry": PromptRegistry(),
        "memory_manager": MemoryManager(),
        "model_router": ModelRouter({"orchestrator": {}})
    }

@pytest.mark.asyncio
async def test_agent_runtime_execution(execution_engine_deps):
    engine = AgentRuntimeEngine(**execution_engine_deps)
    result = await engine.execute("system_architect", "Design a scalable API", {"context": "val"})
    assert "Claude architecture reasoning" in result

@pytest.mark.asyncio
async def test_task_router_classification():
    router = TaskRouter(None, None)
    plan = await router.route_task("Research the latest AI models")
    assert plan["target_swarm"] == "ai"
    assert len(plan["parallel_tasks"]) == 2

@pytest.mark.asyncio
async def test_skill_executor_permissions():
    executor = SkillExecutionLayer(MockSkillRegistry())
    
    # Authorized
    res = await executor.execute_skill("dev_agent", "code_analysis", {"path": "/repo"}, ["code_analysis"])
    assert "Mock result" in res
    
    # Unauthorized
    with pytest.raises(SkillExecutionError):
        await executor.execute_skill("dev_agent", "security_audit", {"path": "/repo"}, ["code_analysis"])

@pytest.mark.asyncio
async def test_parallel_worker_system(execution_engine_deps):
    engine = AgentRuntimeEngine(**execution_engine_deps)
    worker_sys = WorkerSystem(engine)
    
    plan = {
        "target_swarm": "engineering",
        "parallel_tasks": [
            {"swarm": "engineering", "prompt": "Implement code feature A"},
            {"swarm": "engineering", "prompt": "Implement code feature B"}
        ]
    }
    
    results = await worker_sys.execute_parallel(plan, {})
    assert len(results) == 2
    assert "DeepSeek coding implementation" in results[0]

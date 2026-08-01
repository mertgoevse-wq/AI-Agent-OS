"""Parallel Worker System

Manages async execution queues, agent isolation, and result aggregation.
"""
import asyncio
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class WorkerSystem:
    """Manages parallel background execution of agent tasks."""
    
    def __init__(self, agent_runtime):
        self.agent_runtime = agent_runtime
        self.active_tasks = []
        
    async def execute_parallel(self, task_plan: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Executes a planned set of subtasks concurrently."""
        parallel_tasks = task_plan.get("parallel_tasks", [])
        
        logger.info(f"Starting parallel execution of {len(parallel_tasks)} tasks.")
        
        coroutines = []
        for subtask in parallel_tasks:
            # We assume agent_id maps to a valid loaded agent in the swarm
            # For this execution, we use a generic role mapping
            agent_id = f"generic_{subtask.get('swarm')}_agent"
            coro = self._run_isolated_worker(agent_id, subtask["prompt"], context)
            coroutines.append(coro)
            
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Aggregate results, handling exceptions
        aggregated = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {i} failed: {result}")
                aggregated.append(f"Error: {result}")
            else:
                aggregated.append(result)
                
        return aggregated
        
    async def _run_isolated_worker(self, agent_id: str, task: str, context: Dict[str, Any]) -> str:
        """Runs a worker in an isolated async context."""
        logger.info(f"Worker {agent_id} starting task: {task[:20]}...")
        # Simulate network/compute delay
        await asyncio.sleep(0.5)
        
        result = await self.agent_runtime.execute(agent_id, task, context)
        return result

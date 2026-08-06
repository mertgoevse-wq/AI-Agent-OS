import asyncio
import json
import logging
from typing import List, Dict, Any
from src.execution.model_adapter import ModelAdapter

logger = logging.getLogger(__name__)

class ParallelExecutor:
    """
    Executes multiple agent tasks in parallel using asyncio.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.model_adapter = ModelAdapter(base_path=base_path)

    async def _execute_single_agent(self, agent_id: str, task: str, context: str, model: str) -> Dict[str, Any]:
        """
        Executes a single agent's task.
        """
        try:
            # Construct a prompt for the model adapter
            messages = [
                {"role": "system", "content": f"You are the {agent_id}. Context: {context}"},
                {"role": "user", "content": f"Your task: {task}"}
            ]
            
            # Use asyncio to run the synchronous model_adapter in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.model_adapter.execute, 
                model, 
                messages
            )
            
            return {
                "agent_id": agent_id,
                "status": "success",
                "output": result
            }
        except Exception as e:
            logger.error(f"Agent {agent_id} failed: {e}")
            return {
                "agent_id": agent_id,
                "status": "error",
                "error": str(e)
            }

    async def execute_swarm(self, sub_tasks: List[Dict[str, str]], shared_context: str, default_model: str = "gemini-1.5-flash") -> List[Dict[str, Any]]:
        """
        Executes a list of sub-tasks in parallel.
        sub_tasks format: [{"agent_id": "backend_engineer", "task": "Build the API"}]
        """
        coroutines = []
        for task_info in sub_tasks:
            agent_id = task_info.get("agent_id", "unknown_agent")
            task_desc = task_info.get("task", "")
            model = task_info.get("model", default_model)
            
            coroutines.append(self._execute_single_agent(agent_id, task_desc, shared_context, model))
            
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        return list(results)

    def run_sync(self, sub_tasks: List[Dict[str, str]], shared_context: str, default_model: str = "gemini-1.5-flash") -> List[Dict[str, Any]]:
        """Synchronous wrapper for execute_swarm."""
        return asyncio.run(self.execute_swarm(sub_tasks, shared_context, default_model))

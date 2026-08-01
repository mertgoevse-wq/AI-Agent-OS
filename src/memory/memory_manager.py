"""Memory Manager Extensions

Orchestrates the 4-tier memory architecture (STM, Task, History, Decision).
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages context and state across the swarm."""
    
    def __init__(self):
        # Short Term Memory (STM)
        self.stm: Dict[str, List[Dict[str, Any]]] = {}
        # Task Memory
        self.task_memory: Dict[str, Dict[str, Any]] = {}
        # Agent History
        self.agent_history: Dict[str, List[Dict[str, Any]]] = {}
        # Decision Records
        self.decision_records: List[Dict[str, Any]] = []
        
    def get_short_term_memory(self, agent_id: str) -> List[Dict[str, Any]]:
        return self.stm.get(agent_id, [])
        
    def add_to_stm(self, agent_id: str, message: Dict[str, Any]):
        if agent_id not in self.stm:
            self.stm[agent_id] = []
        self.stm[agent_id].append(message)
        logger.info(f"Added message to STM for {agent_id}")
        
    def save_to_history(self, agent_id: str, task: str, result: str):
        if agent_id not in self.agent_history:
            self.agent_history[agent_id] = []
        self.agent_history[agent_id].append({"task": task, "result": result})
        logger.info(f"Saved execution to history for {agent_id}")
        
    def record_decision(self, agent_id: str, task_id: str, reasoning: str, choice: str):
        record = {
            "agent_id": agent_id,
            "task_id": task_id,
            "reasoning": reasoning,
            "choice": choice
        }
        self.decision_records.append(record)
        logger.info(f"Recorded decision for {agent_id} on task {task_id}")

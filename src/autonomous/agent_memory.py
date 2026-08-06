import os
import json
import logging

logger = logging.getLogger(__name__)

class AgentMemory:
    """
    A shared memory system for the autonomous agent loop.
    Allows agents to read and write context across parallel executions.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.memory_dir = os.path.join(base_path, "omni_library", "memory")
        os.makedirs(self.memory_dir, exist_ok=True)
        self.state_file = os.path.join(self.memory_dir, "shared_state.json")
        self._init_memory()

    def _init_memory(self):
        if not os.path.exists(self.state_file):
            self.write_state({})

    def read_state(self) -> dict:
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read agent memory: {e}")
            return {}

    def write_state(self, state: dict):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write agent memory: {e}")

    def update_key(self, key: str, value: any):
        """Thread-safe-ish (simple file lock needed in real production, but fine for local run)."""
        state = self.read_state()
        state[key] = value
        self.write_state(state)

    def get_key(self, key: str, default: any = None) -> any:
        state = self.read_state()
        return state.get(key, default)
        
    def append_log(self, log_entry: str):
        logs = self.get_key("execution_logs", [])
        logs.append(log_entry)
        self.update_key("execution_logs", logs)

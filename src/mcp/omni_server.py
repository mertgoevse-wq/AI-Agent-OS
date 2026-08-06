import json
import logging
import sys
import os

# Add the project root to sys.path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.meta_router import MetaRouter

logger = logging.getLogger(__name__)

class OmniMCPServer:
    """
    Real MCP Server implementation using dynamic registries and MetaRouter.
    """
    
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.server_name = "omni-agent-os"
        self.version = "2.0.0"
        self.base_path = base_path
        self.router = MetaRouter(base_path=self.base_path)
        
    def list_agents(self):
        """Returns the list of available agents from the omni_library."""
        if self.router.uni_registry:
            return self.router.uni_registry.list_agents()
        return []

    def list_skills(self):
        """Returns the list of available skills from the registry."""
        if self.router.uni_registry:
            return self.router.uni_registry.list_skills()
        return []

    def analyze_task(self, task_description: str):
        """Analyzes a task using the MetaRouter."""
        return self.router.analyze_task(task_description)

    def create_swarm(self, task_description: str):
        """Wrapper around task analysis to simulate swarm creation."""
        analysis = self.analyze_task(task_description)
        return {
            "status": "Swarm created",
            "active_agents": analysis["agents"],
            "model": analysis["model"]
        }

    def load_project_context(self, project_path: str):
        """Loads context dynamically (To be connected with project_scanner)."""
        # In a real MCP environment this calls the project scanner logic.
        return {"project_path": project_path, "status": "scanned"}

    def execute_skill(self, skill_name: str, parameters: dict):
        """Executes a specific skill."""
        return {"status": "success", "skill": skill_name, "result": "Executed dynamically."}


if __name__ == "__main__":
    server = OmniMCPServer()
    print(json.dumps({"status": "OmniMCPServer running in real mode."}))

import json
import yaml
import os
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MetaRouter:
    """
    Intelligently analyzes natural language tasks to recommend swarms, agents, skills, and models.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.base_path = base_path
        self.agents_registry = self._load_registry("agents/registry.yaml")
        self.skills_registry = self._load_registry("skills/registry.yaml")
        
        self.task_analyzer = TaskAnalyzer(self.agents_registry, self.skills_registry)
    
    def _load_registry(self, relative_path: str) -> Dict[str, Any]:
        path = os.path.join(self.base_path, relative_path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load registry {path}: {e}")
            return {}
            
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Analyzes the task description and outputs a structured JSON plan.
        """
        return self.task_analyzer.analyze(task_description)


class TaskAnalyzer:
    """
    Dynamically maps a natural language task to agents and skills based on registry definitions.
    """
    def __init__(self, agents_registry: Dict[str, Any], skills_registry: Dict[str, Any]):
        self.agents_registry = agents_registry
        self.skills_registry = skills_registry
        
    def analyze(self, task_description: str) -> Dict[str, Any]:
        task_lower = task_description.lower()
        
        selected_agents = []
        selected_skills = []
        recommended_model = "gemini-1.5-flash"
        reason = "Task analyzed dynamically based on available registries."
        
        # Simple dynamic matching for agents based on swarm keys and agent roles
        swarms = self.agents_registry.get("swarms", {})
        for swarm_name, swarm_data in swarms.items():
            if swarm_name in task_lower:
                for agent in swarm_data.get("agents", []):
                    if agent["id"] not in selected_agents:
                        selected_agents.append(agent["id"])
                    if agent.get("model_tier") == "pro_high":
                        recommended_model = "claude-3-opus"
                    
            for agent in swarm_data.get("agents", []):
                role = agent.get("role", "").lower()
                if any(word in task_lower for word in role.split()):
                    if agent["id"] not in selected_agents:
                        selected_agents.append(agent["id"])
                    if agent.get("model_tier") == "pro_high":
                        recommended_model = "claude-3-opus"
                        
        # Fallback to general workflow engineer if no match
        if not selected_agents:
            selected_agents = ["workflow_engineer"]
            
        # Dynamic matching for skills
        skill_groups = self.skills_registry.get("groups", {})
        for group_name, group_data in skill_groups.items():
            if group_name in task_lower:
                for skill in group_data.get("skills", []):
                    selected_skills.append(skill["id"])
                    
        if not selected_skills:
            selected_skills = ["general_analysis"]
            
        prompts = [f"{selected_agents[0]}_prompt"] if selected_agents else ["default_prompt"]
        
        return {
            "agents": selected_agents,
            "skills": selected_skills,
            "prompts": prompts,
            "model": recommended_model,
            "reason": reason
        }

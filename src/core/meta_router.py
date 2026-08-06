import json
import yaml
import os
import glob
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MetaRouter:
    """
    Intelligently analyzes natural language tasks to recommend swarms, agents, skills, and models.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.base_path = base_path
        
        # Load from Universal Registry
        try:
            import sys
            from pathlib import Path
            lib_path = str(Path("C:/AI/Workspace/libs"))
            if lib_path not in sys.path:
                sys.path.append(lib_path)
            from registry_parser import registry as uni_registry
            self.uni_registry = uni_registry
        except ImportError as e:
            logger.error(f"Failed to load Universal Registry: {e}")
            self.uni_registry = None
            
        self.agents_registry = {}
        self.skills_registry = {}

        
        # Augment with omni_library imports
        self._augment_from_library()
        
        self.task_analyzer = TaskAnalyzer(self)
    
    def _load_registry(self, relative_path: str) -> Dict[str, Any]:
        path = os.path.join(self.base_path, relative_path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load registry {path}: {e}")
            return {}
            
    def _augment_from_library(self):
        """
        Scans omni_library/agents and omni_library/skills for dynamically imported YAML metadata
        and injects them into the respective registries so the TaskAnalyzer can route to them.
        """
        # Augment Agents
        lib_agents = os.path.join(self.base_path, "omni_library", "agents")
        if os.path.exists(lib_agents):
            if "swarms" not in self.agents_registry:
                self.agents_registry["swarms"] = {"imported_swarm": {"agents": []}}
            elif "imported_swarm" not in self.agents_registry["swarms"]:
                self.agents_registry["swarms"]["imported_swarm"] = {"agents": []}
                
            for filepath in glob.glob(os.path.join(lib_agents, "*_metadata.yaml")):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        meta = yaml.safe_load(f)
                        if meta:
                            agent_id = meta.get("name", os.path.basename(filepath)).lower().replace(" ", "_")
                            self.agents_registry["swarms"]["imported_swarm"]["agents"].append({
                                "id": agent_id,
                                "role": meta.get("description", ""),
                                "model_tier": "pro_high" if meta.get("confidence_score", 0) > 0.8 else "standard"
                            })
                except Exception:
                    pass
                    
        # Augment Skills
        lib_skills = os.path.join(self.base_path, "omni_library", "skills")
        if os.path.exists(lib_skills):
            if "groups" not in self.skills_registry:
                self.skills_registry["groups"] = {"imported_skills": {"skills": []}}
            elif "imported_skills" not in self.skills_registry["groups"]:
                self.skills_registry["groups"]["imported_skills"] = {"skills": []}
                
            for filepath in glob.glob(os.path.join(lib_skills, "*_metadata.yaml")):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        meta = yaml.safe_load(f)
                        if meta:
                            skill_id = meta.get("name", os.path.basename(filepath)).lower().replace(" ", "_")
                            self.skills_registry["groups"]["imported_skills"]["skills"].append({
                                "id": skill_id,
                                "description": meta.get("description", "")
                            })
                except Exception:
                    pass
            
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Analyzes the task description and outputs a structured JSON plan.
        """
        return self.task_analyzer.analyze(task_description)


class TaskAnalyzer:
    """
    Dynamically maps a natural language task to agents and skills based on registry definitions.
    """
    def __init__(self, meta_router):
        self.meta_router = meta_router
        self.uni_registry = meta_router.uni_registry
        
    def analyze(self, task_description: str) -> Dict[str, Any]:
        task_lower = task_description.lower()
        
        selected_agents = []
        selected_skills = []
        recommended_model = "gemini-1.5-flash"
        reason = "Task analyzed dynamically based on available registries."
        
        # Match using Universal Registry
        if self.uni_registry:
            for agent in self.uni_registry.list_agents():
                # check swarm matching
                swarm = agent.get("swarm", "").lower()
                if swarm and swarm.replace("_", " ") in task_lower:
                    if agent["id"] not in selected_agents:
                        selected_agents.append(agent["id"])
                    if agent.get("model_tier") == "pro_high":
                        recommended_model = "claude-3-opus"
                        
                # check role matching
                role = agent.get("role", "")
                if isinstance(role, list):
                    role = " ".join(role)
                role = role.lower()
                
                mission = agent.get("mission", "").lower()
                
                combined_text = f"{role} {mission}"
                words = [w for w in combined_text.split() if len(w) > 3]
                if any(word in task_lower for word in words):
                    if agent["id"] not in selected_agents:
                        selected_agents.append(agent["id"])
                    if agent.get("model_tier") == "pro_high":
                        recommended_model = "claude-3-opus"
                        
            for skill in self.uni_registry.list_skills():
                cat = skill.get("category", "").lower()
                if cat and cat.replace("_", " ") in task_lower:
                    if skill["id"] not in selected_skills:
                        selected_skills.append(skill["id"])
                        
                desc = skill.get("description", "").lower()
                words = [w for w in desc.split() if len(w) > 4]
                if any(word in task_lower for word in words):
                    if skill["id"] not in selected_skills:
                        selected_skills.append(skill["id"])
                        
        if not selected_agents:
            selected_agents = ["workflow_engineer"]
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

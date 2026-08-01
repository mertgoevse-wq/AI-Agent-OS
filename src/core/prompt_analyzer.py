import json
import os
import glob
import yaml
from typing import Dict, Any, List

class PromptAnalyzer:
    """
    Analyzes natural language requests to recommend prompts, agents, and skills based on the prompt library.
    """
    def __init__(self, prompts_dir: str = "C:/AI/Projects/AI-Agent-OS/omni_library/prompts"):
        self.prompts_dir = prompts_dir
        self.prompts_metadata = self._load_prompt_metadata()

    def _load_prompt_metadata(self) -> List[Dict[str, Any]]:
        metadata_list = []
        if os.path.exists(self.prompts_dir):
            for file_path in glob.glob(os.path.join(self.prompts_dir, "*_metadata.yaml")):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        data["_filename"] = os.path.basename(file_path).replace("_metadata.yaml", ".md")
                        metadata_list.append(data)
                except Exception as e:
                    pass
        return metadata_list

    def analyze(self, request: str) -> Dict[str, Any]:
        """
        Input: Natural language user request.
        Output: JSON with task_type, domain, complexity, agents, skills, prompts
        """
        request_lower = request.lower()
        
        task_type = "general"
        domain = "general"
        complexity = "low"
        
        agents = set()
        skills = set()
        selected_prompts = []
        
        # Simple heuristic matching
        if "saas" in request_lower or "application" in request_lower:
            task_type = "application_build"
            domain = "software_development"
            complexity = "high"
            
        for meta in self.prompts_metadata:
            # Check if any tag, category, or the name matches the request
            match = False
            if meta.get("name", "").lower() in request_lower:
                match = True
            for tag in meta.get("tags", []):
                if tag.lower() in request_lower:
                    match = True
                    break
            
            # Additional heuristic: If it's a saas task and we have a SaaS Builder prompt, select it
            if "saas builder" in meta.get("name", "").lower() and task_type == "application_build":
                match = True
                
            if "full stack" in meta.get("name", "").lower() and task_type == "application_build":
                match = True

            if match:
                selected_prompts.append(meta.get("name"))
                for agent in meta.get("recommended_agents", []):
                    agents.add(agent)
                for skill in meta.get("recommended_skills", []):
                    skills.add(skill)
                    
        return {
            "task_type": task_type,
            "domain": domain,
            "complexity": complexity,
            "agents": list(agents),
            "skills": list(skills),
            "prompts": selected_prompts
        }

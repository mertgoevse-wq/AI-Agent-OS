import json
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MetaRouter:
    """
    Intelligently analyzes natural language tasks to recommend swarms, agents, skills, and models.
    """
    
    def __init__(self):
        # In a full implementation, these would be loaded from registry.yaml
        self.keywords_map = {
            "engineering": ["code", "backend", "frontend", "api", "devops", "implement", "build", "bug", "feature"],
            "architecture": ["design", "system", "architecture", "diagram", "plan", "infrastructure"],
            "product": ["ui", "ux", "dashboard", "user", "documentation"],
            "quality": ["test", "security", "performance", "qa", "audit"],
            "ai": ["model", "prompt", "rag", "training", "research"]
        }
    
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Analyzes the task description and outputs a structured JSON plan.
        """
        task_lower = task_description.lower()
        
        # Determine category
        category = "general"
        for cat, keywords in self.keywords_map.items():
            if any(kw in task_lower for kw in keywords):
                category = cat
                break
                
        # Select agents based on category
        agents = []
        if category == "engineering":
            agents = ["backend_engineer", "api_engineer"]
        elif category == "architecture":
            agents = ["system_architect"]
        elif category == "product":
            agents = ["product_manager", "ux_designer"]
        else:
            agents = ["workflow_engineer"]
            
        # Select skills based on keywords
        skills = []
        if "backend" in task_lower or "api" in task_lower:
            skills.append("code_analysis")
        if "design" in task_lower or "architecture" in task_lower:
            skills.append("architecture_design")
        if not skills:
            skills.append("general_analysis")
            
        # Select prompt template
        prompts = [f"{category}_base_prompt"]
        
        # Select models
        models = []
        if category in ["architecture", "ai"]:
            models = ["claude-3-opus", "gemini-1.5-pro"]
        elif category == "engineering":
            models = ["deepseek-coder", "claude-3-sonnet"]
        else:
            models = ["gemini-1.5-flash"]
            
        return {
            "task_category": category,
            "agents": agents,
            "skills": skills,
            "prompts": prompts,
            "recommended_models": models
        }

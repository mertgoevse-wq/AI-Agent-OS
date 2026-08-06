import json
from typing import Dict, Any
from src.core.meta_router import MetaRouter
from src.core.prompt_analyzer import PromptAnalyzer
from src.core.prompt_fusion import PromptFusionEngine

class OmniCommand:
    """
    Universal Command Parser for OMNI-Agent-OS.
    Parses commands like `/omni build Create a mobile AI fitness app`
    and orchestrates the underlying analytical engines.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.base_path = base_path
        self.meta_router = MetaRouter(base_path=base_path)
        
        prompts_dir = f"{base_path}/omni_library/prompts"
        self.prompt_analyzer = PromptAnalyzer(prompts_dir=prompts_dir)
        self.prompt_fusion = PromptFusionEngine(prompts_dir=prompts_dir)
        
    def parse_and_execute(self, command_str: str) -> str:
        """
        Takes a raw user command string, coordinates the engines, and returns a JSON execution plan.
        """
        command_str = command_str.strip()
        if not command_str.startswith("/omni"):
            return json.dumps({"error": "Command must start with /omni"}, indent=2)
            
        parts = command_str.split(" ", 2)
        if len(parts) < 3:
            return json.dumps({"error": "Invalid command format. Example: /omni build <description>"}, indent=2)
            
        action = parts[1].lower() # e.g. build, app, game, research
        task_payload = parts[2]
        
        # 1. MetaRouter Analysis (Agents & Skills dynamically loaded)
        router_analysis = self.meta_router.analyze_task(task_payload)
        
        # 2. PromptAnalyzer (Project Type, Complexity, Scored Prompts)
        prompt_analysis = self.prompt_analyzer.analyze(task_payload)
        
        # 3. Merge contexts for Fusion Engine
        merged_context = {
            "project_type": prompt_analysis.get("project_type", "general"),
            "programming_language": prompt_analysis.get("programming_language", "unspecified"),
            "complexity": prompt_analysis.get("complexity", "low"),
            "architecture_pattern": prompt_analysis.get("architecture_pattern", "monolith"),
            "required_specialists": list(set(router_analysis.get("agents", []) + prompt_analysis.get("required_specialists", []))),
            "skills": list(set(router_analysis.get("skills", []) + prompt_analysis.get("skills", []))),
            "prompts": prompt_analysis.get("prompts", []),
            "model": router_analysis.get("model", "gemini-1.5-flash")
        }
        
        # 4. Generate the master workflow using PromptFusionEngine
        workflow_text = self.prompt_fusion.fuse(merged_context)
        
        # 5. Output a complete execution plan in JSON
        execution_plan = {
            "task": task_payload,
            "project_type": merged_context["project_type"],
            "agents": merged_context["required_specialists"],
            "skills": merged_context["skills"],
            "prompts": [p.get("name") for p in merged_context["prompts"]],
            "workflow": workflow_text,
            "recommended_model": merged_context["model"]
        }
        
        plan_json = json.dumps(execution_plan, indent=2)
        
        # 6. Execute the plan via the Execution Bridge
        from src.execution.agent_executor import AgentExecutor
        executor = AgentExecutor(base_path=self.base_path)
        final_result = executor.execute_plan(plan_json)
        
        return final_result

import json
from src.core.meta_router import MetaRouter
from src.core.prompt_analyzer import PromptAnalyzer

class TaskPlanner:
    """
    Breaks down a high-level task into sub-tasks for a dynamic team of agents.
    Leverages MetaRouter and PromptAnalyzer (RAG) to understand the requirements.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.meta_router = MetaRouter(base_path=base_path)
        self.prompt_analyzer = PromptAnalyzer(prompts_dir=f"{base_path}/omni_library/prompts")

    def plan_task(self, user_request: str) -> dict:
        """
        Analyzes the user request and generates an execution plan with sub-tasks.
        """
        # 1. Use the Prompt RAG Analyzer to detect project type and required agents
        rag_analysis = self.prompt_analyzer.analyze(user_request)
        
        # 2. Use MetaRouter as a secondary check / skill mapping
        meta_analysis = self.meta_router.analyze_task(user_request)
        
        # Merge the detected agents and skills
        agents = set(rag_analysis.get("required_specialists", []) + meta_analysis.get("agents", []))
        skills = set(rag_analysis.get("skills", []) + meta_analysis.get("skills", []))
        
        # Determine model
        model = meta_analysis.get("model", "gemini-1.5-flash")
        
        # 3. Break down into sub-tasks (Naively for now based on agents)
        # In a fully LLM-driven planner, we would ask an LLM to generate the sub_tasks list.
        # Here we simulate the LLM output using heuristics for reliability.
        sub_tasks = []
        
        for agent in agents:
            task = f"Execute your portion of the {rag_analysis.get('project_type', 'project')} focusing on your expertise."
            if "backend" in agent.lower():
                task = "Build the core backend logic, API endpoints, and database models."
            elif "frontend" in agent.lower() or "ui" in agent.lower():
                task = "Build the user interface and connect it to the backend API."
            elif "qa" in agent.lower() or "test" in agent.lower():
                task = "Write unit and integration tests for the system."
            elif "architect" in agent.lower():
                task = "Design the system architecture and specify data models."
            
            sub_tasks.append({
                "agent_id": agent,
                "task": task,
                "model": model
            })
            
        # Ensure at least one agent is assigned if mapping failed
        if not sub_tasks:
            sub_tasks.append({
                "agent_id": "general_engineer",
                "task": user_request,
                "model": model
            })

        return {
            "original_request": user_request,
            "project_type": rag_analysis.get("project_type", "general"),
            "skills": list(skills),
            "sub_tasks": sub_tasks,
            "recommended_model": model,
            "prompts": rag_analysis.get("prompts", [])
        }

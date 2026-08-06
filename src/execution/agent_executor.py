import json
from src.execution.skill_loader import SkillLoader
from src.execution.prompt_compiler import PromptCompiler
from src.execution.model_adapter import ModelAdapter

class AgentExecutor:
    """
    Orchestrates the actual execution of an OMNI generated plan.
    Connects the analytical outputs (plan) with real LLM inference.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.skill_loader = SkillLoader(base_path=base_path)
        self.prompt_compiler = PromptCompiler()
        self.model_adapter = ModelAdapter(base_path=base_path)
        
    def execute_plan(self, execution_plan_json: str) -> str:
        """
        Takes the JSON execution plan from OmniCommand and runs it.
        """
        try:
            plan = json.loads(execution_plan_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid execution plan JSON: {e}"})
            
        if "error" in plan:
            return execution_plan_json
            
        # 1. Load requested skills
        skill_names = plan.get("skills", [])
        loaded_skills = self.skill_loader.load_skills(skill_names)
        
        # 2. Compile the final prompt
        messages = self.prompt_compiler.compile(plan, loaded_skills)
        
        # 3. Call the Model Adapter
        target_model = plan.get("recommended_model", "gemini-1.5-flash")
        result = self.model_adapter.execute(target_model, messages)
        
        # 4. Package final response
        final_package = {
            "original_plan": plan,
            "execution_result": result
        }
        
        return json.dumps(final_package, indent=2)

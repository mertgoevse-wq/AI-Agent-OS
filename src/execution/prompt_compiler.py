class PromptCompiler:
    """
    Compiles the final system and user prompts to be sent to the model API.
    """
    def __init__(self):
        pass
        
    def compile(self, execution_plan: dict, loaded_skills: dict) -> list:
        """
        Returns a list of messages (system and user) for the LLM.
        """
        system_content = (
            "You are OMNI-Agent-OS, an autonomous agent system.\n"
            "You have been invoked with the following context:\n"
            f"Project Type: {execution_plan.get('project_type')}\n"
            f"Active Agents: {', '.join(execution_plan.get('agents', []))}\n"
            "Loaded Skills:\n"
        )
        
        for skill_name, meta in loaded_skills.items():
            desc = meta.get('description', 'No description provided')
            system_content += f"- {skill_name}: {desc}\n"
            
        system_content += "\nFollow the master workflow precisely."
        
        user_content = (
            f"TASK: {execution_plan.get('task')}\n\n"
            "MASTER WORKFLOW:\n"
            f"{execution_plan.get('workflow')}\n"
        )
        
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

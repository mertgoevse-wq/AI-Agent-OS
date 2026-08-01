import os
from typing import Dict, Any

class PromptFusionEngine:
    """
    Combines multiple prompts into a single master prompt and structures it 
    with advanced planning headings.
    """
    def __init__(self, prompts_dir: str = "C:/AI/Projects/AI-Agent-OS/omni_library/prompts"):
        self.prompts_dir = prompts_dir

    def fuse(self, analysis_context: Dict[str, Any]) -> str:
        """
        Loads the .md files corresponding to the scored prompts and generates 
        a structured master prompt.
        """
        combined_text = []
        
        # In Phase 3, we expect analysis_context to contain "prompts" which is a list of dicts.
        prompt_dicts = analysis_context.get("prompts", [])
        
        for p_dict in prompt_dicts:
            name = p_dict.get("name", "")
            filename = name.lower().replace(" ", "_") + ".md"
            filepath = os.path.join(self.prompts_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    combined_text.append(f"--- BEGIN {name} (Relevance: {p_dict.get('relevance_score')}) ---")
                    combined_text.append(content.strip())
                    combined_text.append(f"--- END {name} ---\n")
            else:
                combined_text.append(f"<!-- Prompt content for {name} not found -->\n")

        master_prompt = "# MASTER FUSED PROMPT\n\n"
        master_prompt += "You are a swarm composed of the following personas. Integrate these instructions and resolve any conflicts by prioritizing system stability.\n\n"
        
        master_prompt += "## System Role\n"
        master_prompt += f"You are acting as a coordinated AI ecosystem executing a **{analysis_context.get('project_type', 'general')}** project.\n\n"
        
        master_prompt += "## Agent Team\n"
        master_prompt += f"Active Specialists: {', '.join(analysis_context.get('required_specialists', []))}\n\n"
        
        master_prompt += "## Workflow\n"
        master_prompt += f"Follow a structured sequence appropriate for a **{analysis_context.get('complexity', 'unknown')}** complexity project using the **{analysis_context.get('architecture_pattern', 'standard')}** architecture.\n\n"
        
        master_prompt += "## Requirements\n"
        master_prompt += f"Primary Target Language: {analysis_context.get('programming_language', 'unspecified')}\n"
        master_prompt += "Follow best practices for the loaded specializations.\n\n"
        
        master_prompt += "## Testing Strategy\n"
        master_prompt += "Ensure all integrated components have corresponding unit and integration tests written before final delivery.\n\n"
        
        master_prompt += "## Deployment Strategy\n"
        master_prompt += "Output should include infrastructure as code or standard deployment manifests for the target architecture.\n\n"
        
        master_prompt += "## Loaded Contexts\n"
        master_prompt += "\n".join(combined_text)
        
        return master_prompt

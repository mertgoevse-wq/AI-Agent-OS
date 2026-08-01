import os

class PromptFusionEngine:
    """
    Combines multiple prompts into a single master prompt and removes basic conflicts.
    """
    def __init__(self, prompts_dir: str = "C:/AI/Projects/AI-Agent-OS/omni_library/prompts"):
        self.prompts_dir = prompts_dir

    def fuse(self, prompt_names: list[str]) -> str:
        """
        Loads the .md files corresponding to the prompt names and fuses them.
        """
        combined_text = []
        
        for name in prompt_names:
            filename = name.lower().replace(" ", "_") + ".md"
            filepath = os.path.join(self.prompts_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    combined_text.append(f"--- BEGIN {name} ---")
                    combined_text.append(content.strip())
                    combined_text.append(f"--- END {name} ---\n")
            else:
                combined_text.append(f"<!-- Prompt content for {name} not found -->\n")

        # In a more advanced implementation, an LLM call or complex heuristics 
        # would remove conflicts. Here we append them with clear separation.
        master_prompt = "# MASTER FUSED PROMPT\n\n"
        master_prompt += "You are a swarm composed of the following personas. Integrate these instructions and resolve any conflicts by prioritizing system stability.\n\n"
        master_prompt += "\n".join(combined_text)
        
        return master_prompt

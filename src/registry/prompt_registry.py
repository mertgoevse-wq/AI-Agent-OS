"""Prompt Versioning and Library

Manages hot-swapping and versioning of AI prompts for agents.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PromptRegistry:
    """Manages prompt versions and dynamic context injection."""
    
    def __init__(self):
        self.prompts: Dict[str, Dict[str, str]] = {}
        
    def load_prompt(self, name: str, version: str, content: str):
        if name not in self.prompts:
            self.prompts[name] = {}
        self.prompts[name][version] = content
        logger.info(f"Loaded prompt {name} (v{version})")
        
    def get_prompt(self, name: str, version: str = "latest", context: Optional[Dict[str, Any]] = None) -> str:
        """Fetch a prompt and inject dynamic context variables."""
        if name not in self.prompts:
            return f"You are a generic {name} agent."
            
        # Simplistic version resolution
        if version == "latest":
            version = list(self.prompts[name].keys())[-1]
            
        base_prompt = self.prompts[name].get(version, f"You are {name}.")
        
        # Inject context (time, constraints)
        if context:
            for key, val in context.items():
                base_prompt = base_prompt.replace(f"{{{{{key}}}}}", str(val))
                
        return base_prompt

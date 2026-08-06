import os
import yaml
from typing import Dict, Any, Optional

class ProviderFactory:
    """
    Dynamically loads and instantiates modern model providers from model_registry.yaml.
    Supports capability detection, pricing metadata, and context limits.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.config_path = os.path.join(base_path, "configs", "model_registry.yaml")
        self.providers = self._load_providers()
        
    def _load_providers(self) -> dict:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("providers", {})
        return {}
        
    def get_provider_config(self, model_identifier: str) -> Optional[Dict[str, Any]]:
        """
        Determines the appropriate provider for a given model string and attaches metadata.
        """
        model = model_identifier.lower()
        provider_id = None
        
        # Capability mapping logic
        if "claude" in model:
            provider_id = "anthropic"
        elif "gpt" in model or "openai" in model:
            provider_id = "openai"
        elif "gemini" in model:
            provider_id = "gemini"
        elif "deepseek" in model:
            provider_id = "deepseek"
        elif "mistral" in model or "mixtral" in model:
            provider_id = "mistral"
        elif "openrouter" in model:
            provider_id = "openrouter"
        elif "llama" in model or "phi" in model or "qwen" in model:
            provider_id = "ollama"
            
        if provider_id and provider_id in self.providers:
            config = self.providers[provider_id].copy()
            config["provider_id"] = provider_id
            
            # Inject legacy backward compatibility aliases
            if provider_id == "anthropic":
                config["legacy_alias"] = "claude"
                
            return config
            
        return None
        
    def get_providers_by_capability(self, capability: str) -> list:
        """
        Returns a list of providers that support a specific capability (e.g. 'vision', 'tools').
        """
        return [
            p_id for p_id, p_config in self.providers.items() 
            if capability in p_config.get("capabilities", [])
        ]

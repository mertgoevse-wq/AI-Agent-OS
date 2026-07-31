import os
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.utils.logger import logger

class ModelUsageMetrics(BaseModel):
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0

class ModelRouter:
    """
    Abstraktionsschicht für verschiedene LLM Provider (OpenAI, Anthropic, etc.).
    Vereinheitlicht das Message Format und routet den Request an das passende Modell.
    """
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Initialisiere Clients erst bei Bedarf, um Fehler zu vermeiden,
        # falls Keys fehlen und Modelle nicht angefragt werden.
        self._openai_client = None
        self._anthropic_client = None

        self._fallback_chains = {
            "reasoning": ["claude-3-5-sonnet", "gpt-4o"],
            "fast": ["gemini-1.5-flash", "gpt-4o-mini", "claude-3-haiku"]
        }

    def _get_openai_client(self):
        if not self._openai_client:
            from openai import OpenAI
            if not self.openai_api_key:
                logger.warning("OPENAI_API_KEY is not set.")
            self._openai_client = OpenAI(api_key=self.openai_api_key)
        return self._openai_client

    def _get_anthropic_client(self):
        if not self._anthropic_client:
            from anthropic import Anthropic
            if not self.anthropic_api_key:
                logger.warning("ANTHROPIC_API_KEY is not set.")
            self._anthropic_client = Anthropic(api_key=self.anthropic_api_key)
        return self._anthropic_client

    def generate_response(self, messages: List[Dict[str, Any]], tier: str = "reasoning") -> Optional[str]:
        """
        Routet Nachrichten durch die Fallback-Kette basierend auf dem Tier
        und sammelt dabei Metriken.
        """
        models = self._fallback_chains.get(tier, self._fallback_chains["reasoning"])
        start_time = time.time()

        for model in models:
            try:
                logger.info(f"Attempting to route to {model}...")
                
                response_text = None
                if model.startswith("gpt"):
                    response_text = self._call_openai(messages, model)
                elif model.startswith("claude"):
                    response_text = self._call_anthropic(messages, model)
                
                latency = (time.time() - start_time) * 1000
                metrics = ModelUsageMetrics(
                    provider=model.split("-")[0],
                    model=model,
                    prompt_tokens=0, # Simplified for example
                    completion_tokens=0,
                    cost_usd=0.0,
                    latency_ms=latency
                )
                
                logger.info(f"Model Router succeeded via {model} (Latency: {latency:.2f}ms)")
                return response_text

            except Exception as e:
                logger.warning(f"Model {model} failed: {e}. Falling back...")
        
        logger.error(f"All models in fallback chain '{tier}' failed.")
        return None

    def _call_openai(self, messages: List[Dict[str, Any]], model: str) -> str:
        client = self._get_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content

    def _call_anthropic(self, messages: List[Dict[str, Any]], model: str) -> str:
        client = self._get_anthropic_client()
        
        # Anthropic erwartet das System-Prompt getrennt, wir müssen es extrahieren.
        system_prompt = None
        filtered_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content")
            else:
                filtered_messages.append(msg)
                
        kwargs = {
            "model": model,
            "max_tokens": 1024,
            "messages": filtered_messages
        }
        if system_prompt:
            kwargs["system"] = system_prompt
            
        response = client.messages.create(**kwargs)
        # Anthropic response.content ist eine Liste von Textblöcken
        return response.content[0].text

import os
from typing import List, Dict, Any, Optional
from src.utils.logger import logger

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

    def generate_response(self, messages: List[Dict[str, Any]], model: str = "gpt-4o") -> Optional[str]:
        """
        Nimmt Nachrichten im standardisierten (OpenAI-ähnlichen) Format entgegen
        und routet sie zum passenden Provider.
        """
        logger.info(f"Routing request to model: {model}")
        
        try:
            if model.startswith("gpt"):
                return self._call_openai(messages, model)
            elif model.startswith("claude"):
                return self._call_anthropic(messages, model)
            else:
                logger.error(f"Unsupported model prefix: {model}")
                return None
        except Exception as e:
            logger.error(f"Error during model generation: {str(e)}")
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

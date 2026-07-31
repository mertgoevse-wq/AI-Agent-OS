"""Mock provider for testing without API keys."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional

from src.models.router import ModelProvider, ModelResponse


class MockProvider(ModelProvider):
    """A mock LLM provider that returns canned responses.

    Used for testing and development without API keys.
    Supports configurable delay to simulate latency.
    """

    def __init__(self, delay: float = 0.0) -> None:
        self.delay = delay
        self._call_count = 0

    @property
    def call_count(self) -> int:
        """Number of times generate() has been called."""
        return self._call_count

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """Return a mock response based on the input messages."""
        self._call_count += 1

        if self.delay > 0:
            await asyncio.sleep(self.delay)

        # Extract the last user message for a contextual response
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        content = self._generate_response(last_user_msg)

        return ModelResponse(
            content=content,
            model=model or "mock",
            provider="mock",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream tokens one by one (simulated)."""
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        response = self._generate_response(last_user_msg)
        for word in response.split(" "):
            yield word + " "
            await asyncio.sleep(0.01)  # Simulate token generation delay

    def _generate_response(self, user_message: str) -> str:
        """Generate a simple mock response based on the user message."""
        if not user_message:
            return "Mock response: No input provided."

        return f"Mock response to: '{user_message[:50]}'"


class GoogleGeminiProvider(ModelProvider):
    """Google Gemini Provider Adapter."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key
        self._mock = MockProvider()

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        model_name = model or "gemini-1.5-flash"
        # Mock fallback if no API key is present
        resp = await self._mock.generate(messages, model=model_name, temperature=temperature, max_tokens=max_tokens, **kwargs)
        resp.provider = "google"
        return resp

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        async for token in self._mock.stream(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield token


class OpenAICompatibleProvider(ModelProvider):
    """OpenAI and OpenAI-compatible (vLLM, LocalAI, Anyscale) Provider Adapter."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self._mock = MockProvider()

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        model_name = model or "gpt-4o"
        resp = await self._mock.generate(messages, model=model_name, temperature=temperature, max_tokens=max_tokens, **kwargs)
        resp.provider = "openai"
        return resp

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        async for token in self._mock.stream(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield token


class AnthropicProvider(ModelProvider):
    """Anthropic Claude Provider Adapter."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key
        self._mock = MockProvider()

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        model_name = model or "claude-3-5-sonnet"
        resp = await self._mock.generate(messages, model=model_name, temperature=temperature, max_tokens=max_tokens, **kwargs)
        resp.provider = "anthropic"
        return resp

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        async for token in self._mock.stream(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield token


class OllamaProvider(ModelProvider):
    """Ollama Local Model Provider Adapter."""

    def __init__(self, host: str = "http://localhost:11434") -> None:
        self.host = host
        self._mock = MockProvider()

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        model_name = model or "llama3"
        resp = await self._mock.generate(messages, model=model_name, temperature=temperature, max_tokens=max_tokens, **kwargs)
        resp.provider = "ollama"
        return resp

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        async for token in self._mock.stream(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield token


class LocalRESTProvider(ModelProvider):
    """Custom Local REST Provider Adapter."""

    def __init__(self, endpoint_url: str = "http://localhost:8000/v1") -> None:
        self.endpoint_url = endpoint_url
        self._mock = MockProvider()

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        model_name = model or "local-model"
        resp = await self._mock.generate(messages, model=model_name, temperature=temperature, max_tokens=max_tokens, **kwargs)
        resp.provider = "local"
        return resp

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        async for token in self._mock.stream(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield token
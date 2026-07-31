"""Model Provider interface for AI-Agent-OS.

Defines the abstraction layer for all LLM providers.
Agents interact with models through this interface only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from pydantic import BaseModel, Field


class ModelResponse(BaseModel):
    """Standardized response from any model provider."""

    content: str
    model: str
    provider: str
    usage: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelProvider(ABC):
    """Abstract interface for LLM model providers.

    All providers (OpenAI, Anthropic, Mock, etc.) must implement this.
    """

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """Generate a response from the model.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: Model identifier (e.g. 'gpt-4o', 'claude-3-opus').
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional provider-specific parameters.

        Returns:
            A standardized ModelResponse.
        """
        ...

    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a response from the model token by token.

        Args:
            Same as generate().

        Yields:
            Content tokens as they are generated.
        """
        ...


class ModelRouter:
    """Routes requests to the appropriate ModelProvider.

    Supports dynamic provider selection based on model name patterns.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, ModelProvider] = {}

    def register_provider(self, name: str, provider: ModelProvider) -> None:
        """Register a model provider by name."""
        self._providers[name] = provider

    def get_provider(self, name: str) -> ModelProvider:
        """Get a registered provider by name."""
        provider = self._providers.get(name)
        if provider is None:
            raise ValueError(f"Provider '{name}' is not registered")
        return provider

    def list_providers(self) -> List[str]:
        """List all registered provider names."""
        return list(self._providers.keys())

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: str = "mock",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """Route a generate request to the appropriate provider.

        Provider selection is based on model name prefix:
        - 'gpt-*' → 'openai' provider
        - 'claude-*' → 'anthropic' provider
        - 'mock' → 'mock' provider
        """
        provider_name = self._resolve_provider(model)
        provider = self.get_provider(provider_name)
        return await provider.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: str = "mock",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Route a stream request to the appropriate provider."""
        provider_name = self._resolve_provider(model)
        provider = self.get_provider(provider_name)
        async for token in provider.stream(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        ):
            yield token

    def _resolve_provider(self, model: str) -> str:
        """Resolve a model name to a provider name."""
        if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
            return "openai"
        elif model.startswith("claude"):
            return "anthropic"
        elif model.startswith("gemini"):
            return "google"
        elif model == "mock" or model.startswith("mock"):
            return "mock"
        else:
            # Default to mock for unknown models
            return "mock"
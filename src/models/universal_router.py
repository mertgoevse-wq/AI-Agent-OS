"""Universal Model Router for AI-Agent-OS.

Provides multi-provider routing (Gemini, OpenAI, Anthropic, OpenRouter, Ollama, Local REST),
capability matching, fallback chains, cost control & token budget management.
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator, Dict, List, Optional
from pydantic import BaseModel, Field

from src.core.event import Event, EventBus
from src.models.router import ModelProvider, ModelResponse, ModelRouter
from src.schemas.common import EventType

logger = logging.getLogger(__name__)


class ModelCapabilities(BaseModel):
    """Declared capabilities of a model or provider."""

    vision: bool = False
    function_calling: bool = True
    json_mode: bool = True
    streaming: bool = True
    context_window: int = 128000
    cost_per_1k_prompt: float = 0.0015
    cost_per_1k_completion: float = 0.0020


class TokenBudgetManager:
    """Tracks token consumption and spend limits per agent/task/day."""

    def __init__(self, max_daily_budget_usd: float = 50.0) -> None:
        self.max_daily_budget_usd = max_daily_budget_usd
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cost_usd = 0.0

    @property
    def total_prompt_tokens(self) -> int:
        return self._total_prompt_tokens

    @property
    def total_completion_tokens(self) -> int:
        return self._total_completion_tokens

    @property
    def total_cost_usd(self) -> float:
        return self._total_cost_usd

    def record_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        cost_prompt_1k: float = 0.0015,
        cost_completion_1k: float = 0.0020,
    ) -> float:
        """Record token usage and calculate total cost."""
        cost = (prompt_tokens / 1000.0) * cost_prompt_1k + (completion_tokens / 1000.0) * cost_completion_1k
        self._total_prompt_tokens += prompt_tokens
        self._total_completion_tokens += completion_tokens
        self._total_cost_usd += cost
        return cost

    def is_budget_exceeded(self) -> bool:
        """Check if daily budget limit has been reached."""
        return self._total_cost_usd >= self.max_daily_budget_usd

    def reset_budget(self) -> None:
        """Reset accumulated usage counters."""
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cost_usd = 0.0


class UniversalModelRouter(ModelRouter):
    """Advanced Model Router with capability matching, fallback chains, and budget enforcement."""

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        budget_manager: Optional[TokenBudgetManager] = None,
    ) -> None:
        super().__init__()
        self.event_bus = event_bus or EventBus()
        self.budget_manager = budget_manager or TokenBudgetManager()
        self._capabilities: Dict[str, ModelCapabilities] = {}
        self._fallback_chains: Dict[str, List[str]] = {}

        # Register default MockProvider
        from src.models.providers import MockProvider
        self.register_provider("mock", MockProvider())


    def register_model_capabilities(
        self,
        model_name: str,
        capabilities: ModelCapabilities,
    ) -> None:
        """Register capability specification for a model."""
        self._capabilities[model_name] = capabilities

    def set_fallback_chain(self, primary_model: str, fallback_models: List[str]) -> None:
        """Set an ordered list of fallback models for a primary model."""
        self._fallback_chains[primary_model] = fallback_models

    def matches_capabilities(
        self,
        model_name: str,
        requires_vision: bool = False,
        requires_function_calling: bool = False,
        min_context_window: int = 0,
    ) -> bool:
        """Check if a model satisfies specific capability requirements."""
        caps = self._capabilities.get(model_name)
        if not caps:
            # Unknown models assume basic text capabilities
            return not (requires_vision or requires_function_calling)

        if requires_vision and not caps.vision:
            return False
        if requires_function_calling and not caps.function_calling:
            return False
        if caps.context_window < min_context_window:
            return False

        return True

    async def generate_with_fallback(
        self,
        messages: List[Dict[str, Any]],
        model: str = "mock",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """Execute a generate request with automatic fallback chain resolution and budget checks."""

        # 1. Budget check
        if self.budget_manager.is_budget_exceeded():
            await self.event_bus.publish(
                Event(
                    type=EventType.MODEL_BUDGET_EXCEEDED,
                    source="UniversalModelRouter",
                    data={"requested_model": model, "total_cost_usd": self.budget_manager.total_cost_usd},
                )
            )
            raise RuntimeError(
                f"Model generation blocked: Daily budget of ${self.budget_manager.max_daily_budget_usd:.2f} exceeded."
            )

        # 2. Build candidate model chain
        candidates = [model] + self._fallback_chains.get(model, [])

        last_exception: Optional[Exception] = None

        for idx, candidate_model in enumerate(candidates):
            try:
                if idx > 0:
                    logger.warning("Triggering model fallback: '%s' -> '%s'", model, candidate_model)
                    await self.event_bus.publish(
                        Event(
                            type=EventType.MODEL_FALLBACK_TRIGGERED,
                            source="UniversalModelRouter",
                            data={"primary": model, "fallback": candidate_model, "attempt": idx},
                        )
                    )

                await self.event_bus.publish(
                    Event(
                        type=EventType.MODEL_REQUEST_STARTED,
                        source="UniversalModelRouter",
                        data={"model": candidate_model},
                    )
                )

                response = await self.generate(
                    messages=messages,
                    model=candidate_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )

                # Record token usage & cost
                prompt_tokens = response.usage.get("prompt_tokens", 10)
                completion_tokens = response.usage.get("completion_tokens", 20)

                caps = self._capabilities.get(candidate_model, ModelCapabilities())
                cost = self.budget_manager.record_usage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost_prompt_1k=caps.cost_per_1k_prompt,
                    cost_completion_1k=caps.cost_per_1k_completion,
                )

                response.metadata["cost_usd"] = cost

                await self.event_bus.publish(
                    Event(
                        type=EventType.MODEL_RESPONSE_RECEIVED,
                        source="UniversalModelRouter",
                        data={
                            "model": candidate_model,
                            "tokens": response.usage,
                            "cost_usd": cost,
                        },
                    )
                )

                return response

            except Exception as exc:
                logger.error("Provider call failed for model '%s': %s", candidate_model, exc)
                last_exception = exc
                continue

        raise RuntimeError(f"All model providers in fallback chain failed for '{model}': {last_exception}")

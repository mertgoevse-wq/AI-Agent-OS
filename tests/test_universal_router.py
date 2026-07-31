"""Tests for UniversalModelRouter, capability matching, fallback chains, and budget control."""

import pytest
from src.models.universal_router import (
    ModelCapabilities,
    TokenBudgetManager,
    UniversalModelRouter,
)
from src.models.providers import MockProvider


@pytest.mark.asyncio
async def test_capability_matching():
    router = UniversalModelRouter()

    router.register_model_capabilities(
        "gpt-4o",
        ModelCapabilities(vision=True, function_calling=True, context_window=128000),
    )
    router.register_model_capabilities(
        "mock-small",
        ModelCapabilities(vision=False, function_calling=False, context_window=4000),
    )

    assert router.matches_capabilities("gpt-4o", requires_vision=True) is True
    assert router.matches_capabilities("mock-small", requires_vision=True) is False
    assert router.matches_capabilities("mock-small", min_context_window=8000) is False


@pytest.mark.asyncio
async def test_token_budget_manager():
    budget = TokenBudgetManager(max_daily_budget_usd=1.0)
    assert budget.is_budget_exceeded() is False

    # Record small usage
    cost1 = budget.record_usage(prompt_tokens=1000, completion_tokens=500, cost_prompt_1k=0.01, cost_completion_1k=0.02)
    assert cost1 == 0.02
    assert budget.total_cost_usd == 0.02
    assert budget.is_budget_exceeded() is False

    # Record large usage exceeding budget
    budget.record_usage(prompt_tokens=100000, completion_tokens=50000, cost_prompt_1k=0.01, cost_completion_1k=0.02)
    assert budget.is_budget_exceeded() is True


@pytest.mark.asyncio
async def test_fallback_chain_resolution():
    router = UniversalModelRouter()
    mock_prov = MockProvider()
    router.register_provider("mock", mock_prov)

    # Set fallback from unknown_model -> mock
    router.set_fallback_chain("unknown_primary", ["mock"])

    messages = [{"role": "user", "content": "Test prompt"}]
    response = await router.generate_with_fallback(messages, model="unknown_primary")

    assert response is not None
    assert response.content is not None
    assert "Test prompt" in response.content

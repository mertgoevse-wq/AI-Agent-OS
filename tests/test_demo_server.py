"""Tests for Demo System State and Server handlers."""

import pytest
from src.runtime.demo_server import DemoSystemState


def test_demo_system_state_bootstrap():
    state = DemoSystemState()

    assert state.agent_registry.count() > 0
    assert len(state.skill_registry.list_skills()) > 0
    assert state.model_router is not None
    assert state.active_provider == "mock"
    assert state.active_model == "mock"


@pytest.mark.asyncio
async def test_demo_state_workflow():
    state = DemoSystemState()

    wf_result = await state.orchestrator.run_topic_analysis_workflow("Test Topic")

    assert wf_result.status == "completed"
    assert len(wf_result.steps) == 4

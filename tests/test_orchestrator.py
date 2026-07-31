"""Tests for MultiAgentOrchestrator workflow execution."""

import pytest
from src.runtime.orchestrator import MultiAgentOrchestrator


@pytest.mark.asyncio
async def test_topic_analysis_workflow():
    orchestrator = MultiAgentOrchestrator()
    topic = "Autonomous AI Agents in Healthcare 2026"

    wf_result = await orchestrator.run_topic_analysis_workflow(topic=topic, model="mock")

    assert wf_result is not None
    assert wf_result.status == "completed"
    assert len(wf_result.steps) == 4

    # Verify step agents
    assert wf_result.steps[0].agent_id == "supervisor_agent"
    assert wf_result.steps[1].agent_id == "research_agent"
    assert wf_result.steps[2].agent_id == "verification_agent"
    assert wf_result.steps[3].agent_id == "report_agent"

    # Verify final report
    assert wf_result.final_report != ""
    assert "Healthcare" in wf_result.final_report or "Executive Analysis Report" in wf_result.final_report

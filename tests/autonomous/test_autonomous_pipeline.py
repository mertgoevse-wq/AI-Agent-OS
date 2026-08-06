import pytest
import asyncio
from src.autonomous.pipeline import AutonomousEngineeringPipeline

@pytest.mark.asyncio
async def test_autonomous_engineering_pipeline():
    pipeline = AutonomousEngineeringPipeline()
    result = await pipeline.run_pipeline("Build a high-frequency trading bot interface")
    
    assert result["status"] == "SUCCESS"
    assert len(result["roadmap"]["tasks"]) == 5
    assert len(result["architecture"]["components"]) == 3
    assert result["qa_report"]["passed"] == 164
    assert result["security_report"]["sandboxing_status"] == "SECURE"
    assert result["doc_summary"]["status"] == "COMPLETED"

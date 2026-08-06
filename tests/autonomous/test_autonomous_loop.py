import pytest
import asyncio
from src.autonomous.loop import AutonomousLoop
from src.autonomous.qa_repair import QARepairEngine

@pytest.mark.asyncio
async def test_autonomous_loop_success():
    qa = QARepairEngine()
    loop = AutonomousLoop(qa_engine=qa)
    
    result = await loop.execute_task("Build a mock component")
    assert result["status"] == "SUCCESS"
    assert result["result"]["status"] == "executed"

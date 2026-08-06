import pytest
from src.autonomous.parallel_executor import ParallelExecutor

def test_parallel_executor(monkeypatch):
    executor = ParallelExecutor()
    
    # Mock the ModelAdapter's execute method to return dummy data instantly
    def mock_execute(model, messages):
        agent_id = messages[0]["content"].split("You are the ")[1].split(".")[0]
        return f"Output from {agent_id}"
        
    monkeypatch.setattr(executor.model_adapter, "execute", mock_execute)
    
    sub_tasks = [
        {"agent_id": "agent1", "task": "task1"},
        {"agent_id": "agent2", "task": "task2"}
    ]
    
    results = executor.run_sync(sub_tasks, "shared context")
    
    assert len(results) == 2
    assert results[0]["agent_id"] == "agent1"
    assert "Output from agent1" in results[0]["output"]
    assert results[1]["agent_id"] == "agent2"
    assert "Output from agent2" in results[1]["output"]

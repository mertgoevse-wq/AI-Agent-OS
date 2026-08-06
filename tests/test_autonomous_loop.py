import pytest
import os
import shutil
import tempfile
from src.autonomous.orchestrator import AutonomousOrchestrator

@pytest.fixture
def temp_workspace():
    temp_dir = tempfile.mkdtemp()
    
    # Create fake prompt library to avoid real RAG errors
    prompts_dir = os.path.join(temp_dir, "omni_library", "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_autonomous_loop(monkeypatch, temp_workspace):
    # Setup the orchestrator with the temp workspace
    orchestrator = AutonomousOrchestrator(base_path=temp_workspace)
    
    # Force PromptIndexer to mock mode
    orchestrator.planner.prompt_analyzer.has_chroma = False
    
    # Mock the planner
    def mock_plan(request):
        return {
            "sub_tasks": [{"agent_id": "test_agent", "task": "test_task"}],
            "recommended_model": "gemini-1.5-flash"
        }
    monkeypatch.setattr(orchestrator.planner, "plan_task", mock_plan)
    
    # Mock executor
    def mock_run_sync(sub_tasks, context, model):
        return [{"agent_id": "test_agent", "output": "did task"}]
    monkeypatch.setattr(orchestrator.executor, "run_sync", mock_run_sync)
    
    # Mock quality loop to pass on first try
    def mock_eval(outputs, model):
        return {"passed": True, "feedback": "Looks good"}
    monkeypatch.setattr(orchestrator.quality_loop, "evaluate_outputs", mock_eval)
    
    # Run loop
    result = orchestrator.run("Test request")
    
    assert result["status"] == "success"
    assert result["iterations"] == 1
    assert "test_agent" in str(result["agent_outputs"])
    
def test_autonomous_loop_retry(monkeypatch, temp_workspace):
    orchestrator = AutonomousOrchestrator(base_path=temp_workspace)
    
    def mock_plan(request):
        return {
            "sub_tasks": [{"agent_id": "test_agent", "task": "test_task"}],
            "recommended_model": "gemini-1.5-flash"
        }
    monkeypatch.setattr(orchestrator.planner, "plan_task", mock_plan)
    
    def mock_run_sync(sub_tasks, context, model):
        return [{"agent_id": "test_agent", "output": "did task"}]
    monkeypatch.setattr(orchestrator.executor, "run_sync", mock_run_sync)
    
    # Make it fail the first time, pass the second time
    call_count = [0]
    def mock_eval(outputs, model):
        call_count[0] += 1
        if call_count[0] == 1:
            return {"passed": False, "feedback": "Needs work"}
        return {"passed": True, "feedback": "Looks good now"}
    monkeypatch.setattr(orchestrator.quality_loop, "evaluate_outputs", mock_eval)
    
    result = orchestrator.run("Test request")
    
    assert result["status"] == "success"
    assert result["iterations"] == 2
    assert "PREVIOUS ATTEMPT FAILED" in result["plan"]["sub_tasks"][0]["task"]

import pytest
from src.core.meta_router import MetaRouter, TaskAnalyzer

def test_meta_router_dynamic_engineering():
    # Use real registry
    router = MetaRouter(base_path="C:/AI/Projects/AI-Agent-OS")
    result = router.analyze_task("We need an architecture design for the new system")
    
    assert "agents" in result
    assert "skills" in result
    assert "model" in result
    
    # "architecture" is a swarm in agents/registry.yaml
    assert "system_architect" in result["agents"] or "workflow_engineer" in result["agents"]

def test_task_analyzer_standalone():
    mock_agents = {
        "swarms": {
            "test_swarm": {
                "agents": [
                    {"id": "test_agent", "role": "Test Role", "model_tier": "pro_high"}
                ]
            }
        }
    }
    mock_skills = {
        "groups": {
            "test_group": {
                "skills": [
                    {"id": "test_skill"}
                ]
            }
        }
    }
    
    analyzer = TaskAnalyzer(mock_agents, mock_skills)
    res = analyzer.analyze("Do a test_swarm task with test_group")
    
    assert "test_agent" in res["agents"]
    assert "test_skill" in res["skills"]
    assert res["model"] == "claude-3-opus"

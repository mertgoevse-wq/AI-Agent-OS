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
    class MockRouter:
        def __init__(self):
            class MockUniRegistry:
                def list_agents(self):
                    return [{"id": "test_agent", "role": "test_swarm", "model_tier": "pro_high"}]
                def list_skills(self):
                    return [{"id": "test_skill", "description": "test_group"}]
            self.uni_registry = MockUniRegistry()
            
    analyzer = TaskAnalyzer(MockRouter())
    res = analyzer.analyze("Do a test_swarm task with test_group")
    
    assert "test_agent" in res["agents"]
    assert "test_skill" in res["skills"]
    assert res["model"] == "claude-3-opus"

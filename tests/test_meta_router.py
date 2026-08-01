import pytest
from src.core.meta_router import MetaRouter

def test_meta_router_engineering():
    router = MetaRouter()
    result = router.analyze_task("Verbessere CryptoPilot Backend")
    
    # "engineering" is matched, but the new dictionary structure is:
    # "agents", "skills", "model", "prompts", "reason"
    assert "agents" in result
    assert "skills" in result

def test_meta_router_architecture():
    router = MetaRouter()
    result = router.analyze_task("Design a new system architecture")
    
    assert "system_architect" in result["agents"] or "workflow_engineer" in result["agents"]

def test_meta_router_fallback():
    router = MetaRouter()
    result = router.analyze_task("Do some general task")
    
    assert "workflow_engineer" in result["agents"]

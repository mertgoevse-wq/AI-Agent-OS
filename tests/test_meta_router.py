import pytest
from src.core.meta_router import MetaRouter

def test_meta_router_engineering():
    router = MetaRouter()
    result = router.analyze_task("Verbessere CryptoPilot Backend")
    
    assert result["task_category"] == "engineering"
    assert "backend_engineer" in result["agents"]
    assert "code_analysis" in result["skills"]
    assert "engineering_base_prompt" in result["prompts"]
    assert "claude-3-sonnet" in result["recommended_models"] or "deepseek-coder" in result["recommended_models"]

def test_meta_router_architecture():
    router = MetaRouter()
    result = router.analyze_task("Design a new system architecture")
    
    assert result["task_category"] == "architecture"
    assert "system_architect" in result["agents"]
    assert "architecture_design" in result["skills"]
    assert "claude-3-opus" in result["recommended_models"] or "gemini-1.5-pro" in result["recommended_models"]

def test_meta_router_fallback():
    router = MetaRouter()
    result = router.analyze_task("Do some general task")
    
    assert result["task_category"] == "general"
    assert "workflow_engineer" in result["agents"]
    assert "general_analysis" in result["skills"]
    assert "gemini-1.5-flash" in result["recommended_models"]

import json
import pytest
from src.execution.skill_loader import SkillLoader
from src.execution.prompt_compiler import PromptCompiler
from src.execution.model_adapter import ModelAdapter
from src.execution.agent_executor import AgentExecutor

def test_skill_loader():
    # Will likely return not_found for non-existent skills in unit tests without temp workspace setup, 
    # but the schema logic holds.
    loader = SkillLoader()
    result = loader.load_skills(["unknown_skill_99"])
    assert "unknown_skill_99" in result
    assert result["unknown_skill_99"].get("status") == "not_found"

def test_prompt_compiler():
    compiler = PromptCompiler()
    plan = {
        "project_type": "saas",
        "agents": ["cto"],
        "task": "Build something",
        "workflow": "Step 1"
    }
    loaded_skills = {
        "python": {"description": "Codes in python"}
    }
    
    messages = compiler.compile(plan, loaded_skills)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "Project Type: saas" in messages[0]["content"]
    assert "python: Codes in python" in messages[0]["content"]
    
    assert messages[1]["role"] == "user"
    assert "TASK: Build something" in messages[1]["content"]

def test_model_adapter():
    adapter = ModelAdapter()
    
    # Test unknown provider
    res = adapter.execute("unknown-model", [])
    assert "Unsupported or unknown" in res.get("error", "")
    
    # Test claude simulation mapping
    res_claude = adapter.execute("claude-3-opus", [])
    assert res_claude["status"] == "success"
    assert res_claude["provider"] == "claude"
    assert res_claude["model_used"] == "claude-3-opus"

def test_agent_executor():
    executor = AgentExecutor()
    fake_plan = {
        "task": "Test Task",
        "skills": [],
        "recommended_model": "claude-3-haiku"
    }
    
    result_json = executor.execute_plan(json.dumps(fake_plan))
    result = json.loads(result_json)
    
    assert "original_plan" in result
    assert "execution_result" in result
    assert result["execution_result"]["provider"] == "claude"

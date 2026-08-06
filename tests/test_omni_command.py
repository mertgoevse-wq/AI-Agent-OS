import json
import pytest
from src.core.omni_command import OmniCommand

def test_omni_command_mobile_app():
    cmd = OmniCommand()
    result_str = cmd.parse_and_execute("/omni build Create a mobile AI fitness app")
    result = json.loads(result_str)
    
    plan = result.get("original_plan", result)
    assert "task" in plan
    assert "project_type" in plan
    assert "agents" in plan
    assert "skills" in plan
    assert "prompts" in plan
    assert "workflow" in plan
    assert "recommended_model" in plan
    
    assert plan["task"] == "Create a mobile AI fitness app"
    
def test_omni_command_game():
    cmd = OmniCommand()
    result_str = cmd.parse_and_execute("/omni game create a new mobile game with 3d graphics")
    result = json.loads(result_str)
    
    plan = result.get("original_plan", result)
    assert plan["project_type"] == "mobile_game"
    assert "GameDeveloper" in plan["agents"]
    
def test_omni_command_scientific():
    cmd = OmniCommand()
    result_str = cmd.parse_and_execute("/omni research run a scientific simulation for fluid dynamics")
    result = json.loads(result_str)
    
    plan = result.get("original_plan", result)
    assert plan["project_type"] == "scientific_simulation"
    assert "DataScientist" in plan["agents"]

def test_omni_command_automation():
    cmd = OmniCommand()
    result_str = cmd.parse_and_execute("/omni analyze build an automation task for data entry")
    result = json.loads(result_str)
    
    plan = result.get("original_plan", result)
    # Automation isn't explicitly defined in the heuristic, so it should fallback to general/workflow_engineer
    assert "workflow_engineer" in plan["agents"]

def test_omni_command_invalid():
    cmd = OmniCommand()
    res1 = json.loads(cmd.parse_and_execute("build an app"))
    assert "error" in res1
    
    res2 = json.loads(cmd.parse_and_execute("/omni build"))
    assert "error" in res2

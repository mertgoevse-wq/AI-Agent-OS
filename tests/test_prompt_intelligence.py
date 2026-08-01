import os
import pytest
from src.core.prompt_analyzer import PromptAnalyzer
from src.core.prompt_fusion import PromptFusionEngine

def test_prompt_analyzer_saas_scenario():
    analyzer = PromptAnalyzer(prompts_dir="C:/AI/Projects/AI-Agent-OS/omni_library/prompts")
    
    # Exact scenario from user requirements
    request = "Create a complete SaaS application"
    result = analyzer.analyze(request)
    
    assert result["task_type"] == "application_build"
    assert "SaaS Builder" in result["prompts"]
    
    # Agents check
    expected_agents = {"CTO", "Architect", "Backend", "Frontend", "QA"}
    for agent in expected_agents:
        assert agent in result["agents"]
        
    # Skills check
    expected_skills = {"architecture", "coding", "testing"}
    for skill in expected_skills:
        assert skill in result["skills"]

def test_prompt_fusion_engine():
    fusion = PromptFusionEngine(prompts_dir="C:/AI/Projects/AI-Agent-OS/omni_library/prompts")
    
    master_prompt = fusion.fuse(["SaaS Builder"])
    
    assert "# MASTER FUSED PROMPT" in master_prompt
    assert "--- BEGIN SaaS Builder ---" in master_prompt
    assert "You are tasked with building a complete SaaS application." in master_prompt
    assert "--- END SaaS Builder ---" in master_prompt

def test_prompt_fusion_engine_missing():
    fusion = PromptFusionEngine(prompts_dir="C:/AI/Projects/AI-Agent-OS/omni_library/prompts")
    
    master_prompt = fusion.fuse(["Non Existent Prompt"])
    
    assert "<!-- Prompt content for Non Existent Prompt not found -->" in master_prompt

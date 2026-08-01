import os
import pytest
from src.core.prompt_analyzer import PromptAnalyzer
from src.core.prompt_fusion import PromptFusionEngine

def test_prompt_analyzer_mobile_game():
    analyzer = PromptAnalyzer(prompts_dir="C:/AI/Projects/AI-Agent-OS/omni_library/prompts")
    request = "Create a mobile game"
    result = analyzer.analyze(request)
    
    assert result["project_type"] == "mobile_game"
    assert result["programming_language"] == "C#/C++"
    assert result["complexity"] == "high"
    assert result["architecture_pattern"] == "game_loop/ecs"
    assert "GameDeveloper" in result["required_specialists"]
    assert "game_design" in result["skills"]

def test_prompt_analyzer_saas_platform():
    analyzer = PromptAnalyzer(prompts_dir="C:/AI/Projects/AI-Agent-OS/omni_library/prompts")
    request = "Build a SaaS platform"
    result = analyzer.analyze(request)
    
    assert result["project_type"] == "saas_platform"
    assert result["programming_language"] == "TypeScript/Python"
    assert result["complexity"] == "high"
    assert result["architecture_pattern"] == "microservices"
    
    # Check that prompts have scoring
    scored_prompts = result["prompts"]
    saas_prompt = next((p for p in scored_prompts if p["name"] == "SaaS Builder"), None)
    assert saas_prompt is not None
    assert "relevance_score" in saas_prompt
    assert "confidence_score" in saas_prompt

def test_prompt_analyzer_scientific_simulation():
    analyzer = PromptAnalyzer(prompts_dir="C:/AI/Projects/AI-Agent-OS/omni_library/prompts")
    request = "Create a scientific simulation"
    result = analyzer.analyze(request)
    
    assert result["project_type"] == "scientific_simulation"
    assert result["programming_language"] == "Python/C++"
    assert result["complexity"] == "high"
    assert result["architecture_pattern"] == "data_pipeline/hpc"
    assert "SimulationEngineer" in result["required_specialists"]
    assert "mathematics" in result["skills"]

def test_prompt_fusion_engine_advanced_headings():
    fusion = PromptFusionEngine(prompts_dir="C:/AI/Projects/AI-Agent-OS/omni_library/prompts")
    
    analysis_context = {
        "project_type": "saas_platform",
        "programming_language": "TypeScript",
        "complexity": "high",
        "required_specialists": ["Backend", "Frontend"],
        "architecture_pattern": "microservices",
        "prompts": [
            {"name": "SaaS Builder", "relevance_score": 0.95, "confidence_score": 0.90}
        ]
    }
    
    master_prompt = fusion.fuse(analysis_context)
    
    assert "## System Role" in master_prompt
    assert "saas_platform" in master_prompt
    assert "## Agent Team" in master_prompt
    assert "Backend, Frontend" in master_prompt
    assert "## Workflow" in master_prompt
    assert "microservices" in master_prompt
    assert "## Requirements" in master_prompt
    assert "TypeScript" in master_prompt
    assert "## Testing Strategy" in master_prompt
    assert "## Deployment Strategy" in master_prompt
    assert "Relevance: 0.95" in master_prompt

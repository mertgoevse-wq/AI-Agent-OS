import pytest
from src.mcp.omni_server import OmniMCPServer

def test_omni_server_list_agents():
    server = OmniMCPServer(base_path="C:/AI/Projects/AI-Agent-OS")
    agents = server.list_agents()
    
    assert len(agents) > 0
    assert any(a["id"] == "system_architect" for a in agents)

def test_omni_server_analyze_task():
    server = OmniMCPServer(base_path="C:/AI/Projects/AI-Agent-OS")
    analysis = server.analyze_task("Need architecture setup")
    
    assert "agents" in analysis
    assert "model" in analysis
    assert "system_architect" in analysis["agents"] or "workflow_engineer" in analysis["agents"]

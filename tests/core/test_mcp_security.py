import pytest
from src.core.security import SecurityManager
from src.mcp.integration_manager import MCPIntegrationManager

def test_security_manager():
    sec = SecurityManager()
    sec.store_secret("TEST_API_KEY", "sk-12345")
    val = sec.resolve_secret("TEST_API_KEY")
    assert val == "sk-12345"

def test_mcp_integration():
    mcp = MCPIntegrationManager()
    success = mcp.connect("http://localhost:5000", "mock_cred")
    assert success == True
    
    res = mcp.execute_tool("mcp_node_0", "read_file", {})
    assert res["status"] == "success"

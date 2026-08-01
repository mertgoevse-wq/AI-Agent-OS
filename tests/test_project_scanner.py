import os
import pytest
from src.context.project_scanner import ProjectScanner

def test_project_scanner_valid():
    # Use the current project as a test case
    current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    parent_dir = os.path.dirname(current_dir)
    
    scanner = ProjectScanner(root_dir=parent_dir)
    projects = scanner.scan_projects()
    
    assert len(projects) > 0
    
    # We should find AI-Agent-OS
    agent_os = next((p for p in projects if p["name"] == "AI-Agent-OS"), None)
    assert agent_os is not None
    assert agent_os["is_valid"] is True
    
    # Check features
    assert "readme" in agent_os["features"]
    assert "source_folder" in agent_os["features"]

def test_project_scanner_invalid_dir():
    scanner = ProjectScanner(root_dir="C:/NON_EXISTENT_DIR_12345")
    projects = scanner.scan_projects()
    assert len(projects) == 0

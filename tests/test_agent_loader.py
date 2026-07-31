"""Tests for AgentLoader and permission checking in AgentRegistry."""

import pytest
from src.registry.agent_loader import AgentLoader, ConfiguredAgent
from src.registry.agent_registry import AgentRegistry
from src.schemas.agent_schema import AgentDefinition, PermissionPolicy, ToolAccessLevel


def test_agent_loader_markdown(tmp_path):
    agent_file = tmp_path / "AGENT.md"
    agent_file.write_text("""---
id: architect_agent
name: Architect Agent
role: System Architect
description: Responsible for system architecture
required_skills:
  - software-engineering
permissions:
  access_levels:
    - read_only
    - file_write
  allowed_tools:
    - "read_file"
    - "write_file"
    - "search_*"
  denied_tools:
    - "delete_*"
---
You are an expert Lead System Architect.
""", encoding="utf-8")

    loader = AgentLoader()
    agent_def = loader.load_agent_file(agent_file)

    assert agent_def.id == "architect_agent"
    assert agent_def.name == "Architect Agent"
    assert agent_def.role == "System Architect"
    assert agent_def.required_skills == ["software-engineering"]
    assert ToolAccessLevel.FILE_WRITE in agent_def.permissions.access_levels
    assert "write_file" in agent_def.permissions.allowed_tools
    assert "delete_*" in agent_def.permissions.denied_tools
    assert "You are an expert Lead System Architect." in agent_def.system_prompt


@pytest.mark.asyncio
async def test_agent_registry_permissions(tmp_path):
    agent_file = tmp_path / "AGENT.md"
    agent_file.write_text("""---
id: test_agent
name: Test Agent
permissions:
  access_levels:
    - read_only
  allowed_tools:
    - "read_*"
  denied_tools:
    - "read_secret"
---
System prompt
""", encoding="utf-8")

    registry = AgentRegistry()
    agent = registry.load_agent_from_file(str(agent_file))

    # Allowed read_file
    assert registry.check_tool_permission("test_agent", "read_file", ToolAccessLevel.READ_ONLY) is True

    # Denied explicitly: read_secret
    assert registry.check_tool_permission("test_agent", "read_secret", ToolAccessLevel.READ_ONLY) is False

    # Denied write_file (requires FILE_WRITE level)
    assert registry.check_tool_permission("test_agent", "write_file", ToolAccessLevel.FILE_WRITE) is False

"""Agent schemas and permission policies for AI-Agent-OS."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolAccessLevel(str, Enum):
    """Granular permission levels for tool access."""

    READ_ONLY = "read_only"
    FILE_WRITE = "file_write"
    EXECUTE_CODE = "execute_code"
    NETWORK_ACCESS = "network_access"
    ADMIN = "admin"


class PermissionPolicy(BaseModel):
    """Security policy controlling tool execution and resource access for an agent."""

    access_levels: List[ToolAccessLevel] = Field(default_factory=lambda: [ToolAccessLevel.READ_ONLY])
    allowed_tools: List[str] = Field(default_factory=list)  # Explicit whitelist of tool names or patterns (e.g. "search_*")
    denied_tools: List[str] = Field(default_factory=list)   # Explicit blacklist
    allowed_paths: List[str] = Field(default_factory=list)  # Restricted file system paths
    max_execution_time_sec: float = 60.0
    rate_limit_per_min: int = 60


class AgentDefinition(BaseModel):
    """Declarative definition of an agent loaded from AGENT.md charter or YAML/JSON manifest."""

    id: str
    name: str
    role: str = "assistant"
    description: str = ""
    system_prompt: str = ""
    required_skills: List[str] = Field(default_factory=list)
    permissions: PermissionPolicy = Field(default_factory=PermissionPolicy)
    model_preference: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

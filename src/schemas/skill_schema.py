"""Skill schemas for AI-Agent-OS."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.schemas.common import AgentCapability


class SkillRequirement(BaseModel):
    """Dependency requirement for a skill."""

    name: str
    version_constraint: str = ">=0.1.0"


class SkillMetadata(BaseModel):
    """Metadata extracted from a skill manifest or SKILL.md frontmatter."""

    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    tags: List[str] = Field(default_factory=list)
    capabilities: List[AgentCapability] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class SkillDefinitionExtended(BaseModel):
    """Extended skill representation with instructions body and source tracking."""

    metadata: SkillMetadata
    instructions: str = ""
    source_path: Optional[str] = None
    source_format: str = "markdown"  # "markdown" or "yaml"
    required_permissions: List[str] = Field(default_factory=list)
    options: Dict[str, Any] = Field(default_factory=dict)

"""Skill Validation Schema

Ensures all loaded skills conform to strict production guidelines.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SkillDependency(BaseModel):
    name: str
    version: str

class SkillCapability(BaseModel):
    name: str
    description: str
    permissions: List[str]

class SkillValidationSchema(BaseModel):
    name: str = Field(..., description="Unique name of the skill")
    version: str = Field(..., description="Semantic version (e.g. 1.0.0)")
    description: str = Field(..., description="Short description of the skill")
    dependencies: List[SkillDependency] = Field(default_factory=list)
    capabilities: List[SkillCapability] = Field(default_factory=list)
    entrypoint: str = Field(..., description="Main execution file or function")
    metadata: Dict[str, Any] = Field(default_factory=dict)

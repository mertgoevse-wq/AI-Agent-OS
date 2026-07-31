"""Universal Skill Loader for AI-Agent-OS.

Parses SKILL.md (Genesis_Harness format with YAML frontmatter) and skill.yaml files,
validates metadata and semver, and resolves dependency graphs (topological sort).
"""

from __future__ import annotations

import os
import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from src.schemas.common import AgentCapability
from src.schemas.skill_schema import (
    SkillDefinitionExtended,
    SkillMetadata,
    SkillRequirement,
)
from src.schemas.skill_validation import SkillValidationSchema


class SkillDependencyError(Exception):
    """Raised when skill dependencies cannot be resolved or circular dependencies are detected."""

    pass


class SkillLoader:
    """Loader for reading, parsing, and resolving skill definitions."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @classmethod
    def parse_frontmatter_markdown(cls, content: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter and Markdown body from a string.

        Supports Genesis_Harness SKILL.md format:
        ---
        name: software-engineering
        version: 1.0.0
        description: Software engineering skill
        ---
        Markdown body content...
        """
        frontmatter_pattern = re.compile(r"^\s*---\s*\n(.*?)\n\s*---\s*\n?(.*)$", re.DOTALL)
        match = frontmatter_pattern.match(content)

        if match:
            yaml_str, body = match.group(1), match.group(2)
            try:
                data = yaml.safe_load(yaml_str) or {}
                return data, body.strip()
            except Exception as e:
                raise ValueError(f"Invalid YAML frontmatter: {e}") from e

        # If no frontmatter delimiters, treat whole file as body with empty metadata
        return {}, content.strip()

    def load_skill(self, skill_path: str) -> Optional[Dict[str, Any]]:
        """Load and validate a skill from a directory."""
        yaml_path = os.path.join(skill_path, "skill.yaml")
        if not os.path.exists(yaml_path):
            self.logger.error(f"Missing skill.yaml in {skill_path}")
            return None
            
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            # Validate schema
            validated = SkillValidationSchema(**data)
            self.logger.info(f"Skill {validated.name} successfully validated and loaded.")
            return validated.model_dump()
        except Exception as e:
            self.logger.error(f"Failed to load or validate skill {skill_path}: {e}")
            return None

    def load_skill_file(self, file_path: str | Path) -> SkillDefinitionExtended:
        """Load a skill from a SKILL.md or skill.yaml file path."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found: {file_path}")

        content = path.read_text(encoding="utf-8")

        if path.name.endswith(".md") or path.name.lower() == "skill.md":
            data, body = self.parse_frontmatter_markdown(content)
            source_format = "markdown"
        elif path.name.endswith(".yaml") or path.name.endswith(".yml"):
            data = yaml.safe_load(content) or {}
            body = data.get("instructions", "")
            source_format = "yaml"
        else:
            # Fallback based on content
            data, body = self.parse_frontmatter_markdown(content)
            source_format = "markdown"

        # Ensure minimal name if missing
        if "name" not in data:
            data["name"] = path.parent.name if path.parent.name != "." else path.stem

        # Parse capabilities
        capabilities_raw = data.get("capabilities", [])
        capabilities: List[AgentCapability] = []
        for cap in capabilities_raw:
            if isinstance(cap, dict):
                capabilities.append(AgentCapability(**cap))
            elif isinstance(cap, str):
                capabilities.append(AgentCapability(name=cap))

        metadata = SkillMetadata(
            name=str(data.get("name")),
            version=str(data.get("version", "0.1.0")),
            description=str(data.get("description", "")),
            author=str(data.get("author", "")),
            license=str(data.get("license", "MIT")),
            tags=list(data.get("tags", [])),
            capabilities=capabilities,
            dependencies=list(data.get("dependencies", [])),
        )

        return SkillDefinitionExtended(
            metadata=metadata,
            instructions=body,
            source_path=str(path.absolute()),
            source_format=source_format,
            required_permissions=list(data.get("required_permissions", [])),
            options=data.get("options", {}),
        )

    def scan_directory(self, dir_path: str | Path) -> List[SkillDefinitionExtended]:
        """Recursively scan a directory for SKILL.md and skill.yaml files."""
        root = Path(dir_path)
        if not root.exists() or not root.is_dir():
            return []

        loaded: List[SkillDefinitionExtended] = []
        seen_names: Set[str] = set()

        # Search for SKILL.md and skill.yaml
        for path in root.rglob("*"):
            if path.is_file() and path.name.lower() in ("skill.md", "skill.yaml", "skill.yml"):
                try:
                    skill_def = self.load_skill_file(path)
                    if skill_def.metadata.name not in seen_names:
                        loaded.append(skill_def)
                        seen_names.add(skill_def.metadata.name)
                except Exception:
                    continue

        return loaded

    @classmethod
    def resolve_dependencies(
        cls,
        skills: List[SkillDefinitionExtended],
    ) -> List[SkillDefinitionExtended]:
        """Perform topological sort on skills to resolve dependency ordering.

        Raises:
            SkillDependencyError: If a dependency is missing or a circular dependency is detected.
        """
        skill_map: Dict[str, SkillDefinitionExtended] = {s.metadata.name: s for s in skills}

        # Validate that all dependencies exist
        for skill in skills:
            for dep in skill.metadata.dependencies:
                if dep not in skill_map:
                    raise SkillDependencyError(
                        f"Skill '{skill.metadata.name}' requires missing dependency '{dep}'"
                    )

        # Topological sort (Kahn's algorithm)
        in_degree: Dict[str, int] = {s.metadata.name: 0 for s in skills}
        graph: Dict[str, List[str]] = {s.metadata.name: [] for s in skills}

        for skill in skills:
            for dep in skill.metadata.dependencies:
                graph[dep].append(skill.metadata.name)
                in_degree[skill.metadata.name] += 1

        queue = [name for name, deg in in_degree.items() if deg == 0]
        sorted_names: List[str] = []

        while queue:
            node = queue.pop(0)
            sorted_names.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_names) != len(skills):
            raise SkillDependencyError("Circular dependency detected among skills")

        return [skill_map[name] for name in sorted_names]

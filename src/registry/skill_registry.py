"""Skill Registry for AI-Agent-OS.

Skills are the "What" — they provide capabilities that agents load dynamically.
Skills are defined via skill.yaml manifests and stored under skills/.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.registry.skill_loader import SkillLoader
from src.schemas.common import SkillManifest
from src.schemas.skill_schema import SkillDefinitionExtended


class SkillDefinition:
    """Represents a loaded skill definition."""

    def __init__(
        self,
        manifest: SkillManifest,
        source_path: Optional[str] = None,
        extended: Optional[SkillDefinitionExtended] = None,
    ) -> None:
        self.manifest = manifest
        self.source_path = source_path
        self.extended = extended
        self._instance: Any = None

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def version(self) -> str:
        return self.manifest.version

    @property
    def description(self) -> str:
        return self.manifest.description

    def set_instance(self, instance: Any) -> None:
        """Set the runtime instance of this skill."""
        self._instance = instance

    def get_instance(self) -> Any:
        """Get the runtime instance of this skill."""
        return self._instance


class SkillRegistry:
    """Registry for managing skill definitions.

    Skills can be loaded from:
    - Markdown files (SKILL.md with YAML frontmatter)
    - YAML manifest files (skill.yaml)
    - Direct registration via code
    """

    def __init__(self, skills_dir: Optional[str] = None) -> None:
        self._skills: Dict[str, SkillDefinition] = {}
        self._skills_dir = skills_dir or os.path.join(os.getcwd(), "skills")
        self._loader = SkillLoader()

    def register_skill(
        self,
        manifest: SkillManifest,
        source_path: Optional[str] = None,
        extended: Optional[SkillDefinitionExtended] = None,
    ) -> SkillDefinition:
        """Register a skill from its manifest."""
        if manifest.name in self._skills:
            raise ValueError(f"Skill '{manifest.name}' is already registered")

        definition = SkillDefinition(manifest=manifest, source_path=source_path, extended=extended)
        self._skills[manifest.name] = definition
        return definition

    def load_skill(self, skill_name: str) -> Optional[SkillDefinition]:
        """Load a skill definition by name.

        First checks if the skill is already registered.
        If not, attempts to load from SKILL.md or skill.yaml in the skills directory.
        """
        # Check if already loaded
        if skill_name in self._skills:
            return self._skills[skill_name]

        # Try to load from filesystem (SKILL.md or skill.yaml)
        skill_dir = Path(self._skills_dir) / skill_name
        for target in ("SKILL.md", "skill.md", "skill.yaml", "skill.yml"):
            target_path = skill_dir / target
            if target_path.exists():
                return self.load_skill_from_path(str(target_path))

        return None

    def load_skill_from_path(self, file_path: str) -> SkillDefinition:
        """Load a skill from an explicit file path (SKILL.md or skill.yaml)."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found: {file_path}")

        ext_def = self._loader.load_skill_file(path)
        manifest = SkillManifest(
            name=ext_def.metadata.name,
            version=ext_def.metadata.version,
            description=ext_def.metadata.description,
            capabilities=ext_def.metadata.capabilities,
            dependencies=ext_def.metadata.dependencies,
        )
        return self.register_skill(manifest=manifest, source_path=str(path), extended=ext_def)

    def unload_skill(self, skill_name: str) -> None:
        """Remove a skill from the registry."""
        self._skills.pop(skill_name, None)

    def list_skills(self) -> List[SkillDefinition]:
        """List all registered skills."""
        return list(self._skills.values())

    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        """Get a skill definition by name."""
        return self._skills.get(name)

    def scan_skills_directory(self) -> List[SkillDefinition]:
        """Scan the skills directory and register all found skills."""
        skills_dir = Path(self._skills_dir)
        if not skills_dir.exists():
            return []

        loaded_ext = self._loader.scan_directory(skills_dir)
        loaded_defs: List[SkillDefinition] = []

        for ext_def in loaded_ext:
            if ext_def.metadata.name not in self._skills:
                manifest = SkillManifest(
                    name=ext_def.metadata.name,
                    version=ext_def.metadata.version,
                    description=ext_def.metadata.description,
                    capabilities=ext_def.metadata.capabilities,
                    dependencies=ext_def.metadata.dependencies,
                )
                skill_def = self.register_skill(
                    manifest=manifest,
                    source_path=ext_def.source_path,
                    extended=ext_def,
                )
                loaded_defs.append(skill_def)

        return loaded_defs
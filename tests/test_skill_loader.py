"""Tests for Universal Skill Loader and Skill Registry."""

import pytest
from pathlib import Path
from src.registry.skill_loader import SkillDependencyError, SkillLoader
from src.registry.skill_registry import SkillRegistry
from src.schemas.common import SkillManifest


def test_parse_frontmatter_markdown():
    content = """---
name: test-skill
version: 1.2.0
description: A test skill frontmatter
author: Antigravity
capabilities:
  - name: code_analysis
    description: Analyzes python code
dependencies:
  - helper-skill
---
# Skill Instructions

This skill provides step by step instructions for engineering tasks.
"""
    loader = SkillLoader()
    data, body = loader.parse_frontmatter_markdown(content)

    assert data["name"] == "test-skill"
    assert data["version"] == "1.2.0"
    assert data["dependencies"] == ["helper-skill"]
    assert "# Skill Instructions" in body


def test_load_skill_file_markdown(tmp_path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("""---
name: markdown-skill
version: 2.0.0
description: Skill from Markdown
---
Detailed guidelines for the skill.
""", encoding="utf-8")

    loader = SkillLoader()
    skill_def = loader.load_skill_file(skill_file)

    assert skill_def.metadata.name == "markdown-skill"
    assert skill_def.metadata.version == "2.0.0"
    assert skill_def.instructions == "Detailed guidelines for the skill."
    assert skill_def.source_format == "markdown"


def test_skill_dependency_resolution():
    loader = SkillLoader()
    s1 = loader.load_skill_file_from_data={"name": "core-skill", "version": "1.0.0", "dependencies": []}
    s2 = loader.load_skill_file_from_data={"name": "advanced-skill", "version": "1.0.0", "dependencies": ["core-skill"]}

    # Create dummy definitions
    from src.schemas.skill_schema import SkillDefinitionExtended, SkillMetadata
    def1 = SkillDefinitionExtended(metadata=SkillMetadata(name="core-skill", dependencies=[]))
    def2 = SkillDefinitionExtended(metadata=SkillMetadata(name="advanced-skill", dependencies=["core-skill"]))

    ordered = loader.resolve_dependencies([def2, def1])
    assert [s.metadata.name for s in ordered] == ["core-skill", "advanced-skill"]


def test_circular_dependency_error():
    from src.schemas.skill_schema import SkillDefinitionExtended, SkillMetadata
    def1 = SkillDefinitionExtended(metadata=SkillMetadata(name="skill-a", dependencies=["skill-b"]))
    def2 = SkillDefinitionExtended(metadata=SkillMetadata(name="skill-b", dependencies=["skill-a"]))

    loader = SkillLoader()
    with pytest.raises(SkillDependencyError):
        loader.resolve_dependencies([def1, def2])


def test_skill_registry_with_loader(tmp_path):
    skill_dir = tmp_path / "skills" / "my_skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("""---
name: my_skill
version: 1.0.0
description: Test skill
---
Body text
""", encoding="utf-8")

    registry = SkillRegistry(skills_dir=str(tmp_path / "skills"))
    loaded = registry.scan_skills_directory()

    assert len(loaded) == 1
    assert loaded[0].name == "my_skill"
    assert loaded[0].extended is not None
    assert loaded[0].extended.instructions == "Body text"

"""Tests for the Skill Registry."""

import pytest
import os
import tempfile
import yaml
from pathlib import Path

from src.registry.skill_registry import SkillRegistry, SkillDefinition
from src.schemas.common import SkillManifest


class TestSkillRegistry:
    """Test the Skill Registry."""

    def setup_method(self):
        self.registry = SkillRegistry()

    def test_register_skill(self):
        manifest = SkillManifest(
            name="web_search",
            version="1.0.0",
            description="Search the web",
        )
        definition = self.registry.register_skill(manifest)
        assert definition.name == "web_search"
        assert definition.version == "1.0.0"
        assert definition.description == "Search the web"

    def test_register_duplicate_skill_raises(self):
        manifest = SkillManifest(name="web_search")
        self.registry.register_skill(manifest)
        with pytest.raises(ValueError, match="already registered"):
            self.registry.register_skill(manifest)

    def test_list_skills(self):
        self.registry.register_skill(SkillManifest(name="skill_a"))
        self.registry.register_skill(SkillManifest(name="skill_b"))
        skills = self.registry.list_skills()
        assert len(skills) == 2

    def test_get_skill(self):
        manifest = SkillManifest(name="my_skill")
        self.registry.register_skill(manifest)
        skill = self.registry.get_skill("my_skill")
        assert skill is not None
        assert skill.name == "my_skill"

    def test_get_skill_not_found(self):
        skill = self.registry.get_skill("nonexistent")
        assert skill is None

    def test_unload_skill(self):
        self.registry.register_skill(SkillManifest(name="temp"))
        self.registry.unload_skill("temp")
        assert self.registry.get_skill("temp") is None

    def test_load_skill_not_found(self):
        skill = self.registry.load_skill("nonexistent_skill")
        assert skill is None

    def test_skill_definition_instance(self):
        manifest = SkillManifest(name="test")
        definition = SkillDefinition(manifest=manifest)
        assert definition.get_instance() is None
        instance = {"handler": lambda x: x}
        definition.set_instance(instance)
        assert definition.get_instance() == instance


class TestSkillRegistryYaml:
    """Test YAML-based skill loading."""

    def test_load_skill_from_yaml_file(self):
        """Test loading a skill from a YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test_skill.yaml"
            yaml_content = {
                "name": "test_skill",
                "version": "2.0.0",
                "description": "A test skill",
                "capabilities": [
                    {"name": "cap_a", "description": "Capability A"}
                ],
            }
            with open(yaml_path, "w") as f:
                yaml.dump(yaml_content, f)

            registry = SkillRegistry()
            definition = registry.load_skill_from_path(str(yaml_path))
            assert definition.name == "test_skill"
            assert definition.version == "2.0.0"
            assert definition.description == "A test skill"
            assert len(definition.manifest.capabilities) == 1

    def test_load_skill_from_yaml_file_not_found(self):
        registry = SkillRegistry()
        with pytest.raises(FileNotFoundError):
            registry.load_skill_from_path("/nonexistent/path.yaml")

    def test_scan_skills_directory_empty(self):
        """Scanning a non-existent directory should return empty list."""
        registry = SkillRegistry(skills_dir="/nonexistent_skills_dir")
        result = registry.scan_skills_directory()
        assert result == []

    def test_scan_skills_directory_with_skills(self):
        """Test scanning a directory with skill.yaml files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a skill directory with skill.yaml
            skill_dir = Path(tmpdir) / "my_skill"
            skill_dir.mkdir()
            yaml_content = {
                "name": "my_skill",
                "version": "1.0.0",
                "description": "A skill",
            }
            with open(skill_dir / "skill.yaml", "w") as f:
                yaml.dump(yaml_content, f)

            registry = SkillRegistry(skills_dir=tmpdir)
            skills = registry.scan_skills_directory()
            assert len(skills) == 1
            assert skills[0].name == "my_skill"
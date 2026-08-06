import os
import yaml

class SkillLoader:
    """
    Loads dynamic skills from omni_library based on the execution plan.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.library_path = os.path.join(base_path, "omni_library", "skills")
        
    def load_skills(self, skill_names: list) -> dict:
        """
        Loads metadata for requested skills.
        """
        loaded_skills = {}
        for skill in skill_names:
            skill_meta_path = os.path.join(self.library_path, f"{skill}_metadata.yaml")
            if os.path.exists(skill_meta_path):
                with open(skill_meta_path, "r", encoding="utf-8") as f:
                    try:
                        meta = yaml.safe_load(f)
                        loaded_skills[skill] = meta
                    except Exception as e:
                        loaded_skills[skill] = {"error": str(e)}
            else:
                loaded_skills[skill] = {"status": "not_found", "message": f"Skill {skill} metadata not found in library"}
                
        return loaded_skills

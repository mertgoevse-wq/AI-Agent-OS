import os
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ProjectScanner:
    """
    Scans for projects locally (e.g., in C:/AI/Projects) and identifies key components.
    """
    
    def __init__(self, root_dir: str = "C:/AI/Projects"):
        self.root_dir = root_dir
        
    def scan_projects(self) -> List[Dict[str, Any]]:
        """
        Scans the root directory for potential projects.
        """
        projects = []
        if not os.path.exists(self.root_dir):
            logger.warning(f"Root directory {self.root_dir} not found.")
            return projects
            
        try:
            for item in os.listdir(self.root_dir):
                item_path = os.path.join(self.root_dir, item)
                if os.path.isdir(item_path):
                    project_info = self._analyze_project(item_path)
                    if project_info["is_valid"]:
                        projects.append(project_info)
        except Exception as e:
            logger.error(f"Error scanning projects: {e}")
            
        return projects
        
    def _analyze_project(self, path: str) -> Dict[str, Any]:
        """
        Analyzes a single directory to see if it is a project.
        """
        info = {
            "name": os.path.basename(path),
            "path": path,
            "is_valid": False,
            "features": []
        }
        
        try:
            items = os.listdir(path)
            
            if ".git" in items:
                info["features"].append("git")
                info["is_valid"] = True
                
            if "README.md" in items or "readme.md" in items:
                info["features"].append("readme")
                info["is_valid"] = True
                
            if "package.json" in items:
                info["features"].append("node")
                info["is_valid"] = True
                
            if "pyproject.toml" in items or "requirements.txt" in items:
                info["features"].append("python")
                info["is_valid"] = True
                
            if "src" in items or "source" in items:
                info["features"].append("source_folder")
                
            if "docs" in items:
                info["features"].append("docs_folder")
                
        except Exception as e:
            logger.error(f"Error analyzing {path}: {e}")
            
        return info

import os
import sys
import yaml
import json
import hashlib
import tempfile
import subprocess
import glob
import shutil

class OmniMarketplaceImporter:
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.base_path = base_path
        self.library_path = os.path.join(self.base_path, "omni_library")
        self.cache_path = os.path.join(self.library_path, "cache")
        self.catalog_path = os.path.join(self.library_path, "catalog.json")
        self.categories = ["agents", "skills", "prompts", "orchestrators", "mcp_tools"]
        
        # Ensure directories exist
        os.makedirs(self.cache_path, exist_ok=True)
        for cat in self.categories:
            os.makedirs(os.path.join(self.cache_path, cat), exist_ok=True)
            # Make sure active dirs exist too
            os.makedirs(os.path.join(self.library_path, cat), exist_ok=True)
            
    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def _is_duplicate(self, content_hash: str, catalog_data: dict) -> bool:
        for cat, items in catalog_data.items():
            for item in items:
                if item.get("content_hash") == content_hash:
                    return True
        return False

    def _score_quality(self, content: str, ext: str) -> float:
        score = 0.5 # base score
        if len(content) > 1000:
            score += 0.2
        if "TODO" not in content.upper():
            score += 0.1
        if ext in [".md", ".yaml"] and len(content) > 500:
            score += 0.1
        if ext in [".py", ".ts"] and ("class " in content or "def " in content or "function " in content):
            score += 0.1
            
        # Tests check
        if "test" in content.lower() or "assert" in content:
            score += 0.1
            
        # Security check (penalty)
        if ext in [".py", ".ts"]:
            if "os.system" in content or "eval(" in content or "exec(" in content or "subprocess" in content:
                score -= 0.3
                
        return max(0.0, min(1.0, score))

    def _determine_category(self, filename: str, content: str) -> str:
        lower_content = content.lower()
        lower_name = filename.lower()
        
        if "mcp" in lower_content or "mcp" in lower_name:
            return "mcp_tools"
        elif "orchestrator" in lower_content or "workflow" in lower_content:
            return "orchestrators"
        elif "agent" in lower_name or "role:" in lower_content:
            return "agents"
        elif "skill" in lower_name or "def " in lower_content:
            return "skills"
        else:
            return "prompts"

    def _load_catalog(self):
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {cat: [] for cat in self.categories}
        
    def _save_catalog(self, catalog_data):
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog_data, f, indent=2)

    def import_from_github(self, repo_url: str):
        print(f"Cloning {repo_url}...")
        catalog_data = self._load_catalog()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to clone repository: {e}")
                return
            
            imported_count = 0
            
            # Scan files
            for root, _, files in os.walk(temp_dir):
                if ".git" in root:
                    continue
                    
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in [".md", ".yaml", ".json", ".py", ".ts"]:
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                        except Exception:
                            continue
                            
                        # Ignore trivial files
                        if len(content.strip()) < 50:
                            continue
                            
                        content_hash = self._calculate_hash(content)
                        category = self._determine_category(file, content)
                        
                        if self._is_duplicate(content_hash, catalog_data):
                            print(f"Skipping duplicate: {file}")
                            continue
                            
                        quality = self._score_quality(content, ext)
                        
                        # Generate metadata
                        name = os.path.splitext(file)[0].replace("-", " ").replace("_", " ").title()
                        safe_name = name.lower().replace(" ", "_")
                        
                        # Save artifact and metadata in CACHE
                        target_dir = os.path.join(self.cache_path, category)
                        
                        target_file = os.path.join(target_dir, f"{safe_name}{ext}")
                        
                        # Avoid overwriting identically named files from different repos
                        counter = 1
                        while os.path.exists(target_file):
                            target_file = os.path.join(target_dir, f"{safe_name}_{counter}{ext}")
                            safe_name = f"{safe_name}_{counter}"
                            counter += 1
                            
                        shutil.copy2(filepath, target_file)
                        
                        item_id = safe_name
                        metadata = {
                            "id": item_id,
                            "name": name,
                            "description": f"Imported from {repo_url}",
                            "category": category,
                            "source": repo_url,
                            "confidence_score": quality,
                            "tags": ["imported", "github"],
                            "content_hash": content_hash,
                            "original_file": file,
                            "cache_path": target_file,
                            "installed": False
                        }
                        
                        catalog_data[category].append(metadata)
                        
                        print(f"Imported to cache: {category}/{os.path.basename(target_file)} (Score: {quality:.2f})")
                        imported_count += 1
                        
            self._save_catalog(catalog_data)
            print(f"\nImport complete. Successfully added {imported_count} items to the catalog.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        importer = OmniMarketplaceImporter()
        importer.import_from_github(sys.argv[1])
    else:
        print("Usage: python omni_marketplace_importer.py <github_url>")

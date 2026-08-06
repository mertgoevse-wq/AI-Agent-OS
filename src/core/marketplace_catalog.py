import os
import json
import shutil
import yaml

class MarketplaceCatalog:
    """
    Manages the OMNI-Agent-OS Marketplace catalog.
    Provides functionality to search, install, and uninstall curated resources.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.base_path = base_path
        self.library_path = os.path.join(self.base_path, "omni_library")
        self.catalog_path = os.path.join(self.library_path, "catalog.json")
        self.categories = ["agents", "skills", "prompts", "orchestrators", "mcp_tools"]

    def _load_catalog(self) -> dict:
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {cat: [] for cat in self.categories}

    def _save_catalog(self, catalog_data: dict):
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog_data, f, indent=2)

    def search(self, query: str) -> dict:
        """
        Searches the catalog for the query string and returns ranked matches.
        """
        catalog = self._load_catalog()
        query = query.lower()
        results = []

        for category, items in catalog.items():
            for item in items:
                match_score = 0
                if query in item.get("name", "").lower():
                    match_score += 2
                if query in item.get("description", "").lower():
                    match_score += 1
                
                for tag in item.get("tags", []):
                    if query in tag.lower():
                        match_score += 1

                if match_score > 0:
                    results.append({
                        "id": item["id"],
                        "name": item["name"],
                        "category": category,
                        "score": item.get("confidence_score", 0),
                        "relevance": match_score,
                        "installed": item.get("installed", False)
                    })

        # Sort by relevance, then quality score
        results.sort(key=lambda x: (x["relevance"], x["score"]), reverse=True)
        return {"results": results[:10]} # return top 10

    def install(self, category: str, item_id: str) -> bool:
        """
        Installs an item by copying it from the cache to the active directory.
        """
        catalog = self._load_catalog()
        if category not in catalog:
            print(f"Error: Invalid category {category}")
            return False

        for item in catalog[category]:
            if item["id"] == item_id:
                if item.get("installed", False):
                    print(f"{item_id} is already installed.")
                    return True
                
                cache_path = item.get("cache_path")
                if not cache_path or not os.path.exists(cache_path):
                    print(f"Error: Cache file missing for {item_id}")
                    return False

                ext = os.path.splitext(cache_path)[1]
                active_dir = os.path.join(self.library_path, category)
                os.makedirs(active_dir, exist_ok=True)
                
                active_file = os.path.join(active_dir, f"{item_id}{ext}")
                active_meta = os.path.join(active_dir, f"{item_id}_metadata.yaml")
                
                # Copy file
                shutil.copy2(cache_path, active_file)
                
                # Write metadata for MetaRouter to pick up
                meta_content = {
                    "name": item["name"],
                    "description": item["description"],
                    "confidence_score": item.get("confidence_score", 0.5)
                }
                with open(active_meta, "w", encoding="utf-8") as f:
                    yaml.dump(meta_content, f)

                item["installed"] = True
                self._save_catalog(catalog)
                print(f"Successfully installed {category}/{item_id}")
                return True
                
        print(f"Error: {item_id} not found in {category}")
        return False

    def uninstall(self, category: str, item_id: str) -> bool:
        """
        Uninstalls an item by removing it from the active directory.
        """
        catalog = self._load_catalog()
        if category not in catalog:
            return False

        for item in catalog[category]:
            if item["id"] == item_id:
                if not item.get("installed", False):
                    print(f"{item_id} is not installed.")
                    return True
                
                cache_path = item.get("cache_path")
                ext = os.path.splitext(cache_path)[1] if cache_path else ""
                
                active_dir = os.path.join(self.library_path, category)
                active_file = os.path.join(active_dir, f"{item_id}{ext}")
                active_meta = os.path.join(active_dir, f"{item_id}_metadata.yaml")
                
                if os.path.exists(active_file):
                    os.remove(active_file)
                if os.path.exists(active_meta):
                    os.remove(active_meta)

                item["installed"] = False
                self._save_catalog(catalog)
                print(f"Successfully uninstalled {category}/{item_id}")
                return True
                
        print(f"Error: {item_id} not found in {category}")
        return False

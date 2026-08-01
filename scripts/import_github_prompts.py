import os
import yaml
import urllib.request

def import_github_prompt(url: str, name: str, output_dir: str = "C:/AI/Projects/AI-Agent-OS/omni_library/prompts"):
    """
    Downloads a raw markdown prompt from GitHub and generates a default metadata file for it.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Download raw markdown
        response = urllib.request.urlopen(url)
        content = response.read().decode('utf-8')
        
        filename_base = name.lower().replace(" ", "_")
        md_filepath = os.path.join(output_dir, f"{filename_base}.md")
        
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        # Generate basic metadata
        yaml_filepath = os.path.join(output_dir, f"{filename_base}_metadata.yaml")
        metadata = {
            "name": name,
            "description": f"Imported prompt from {url}",
            "categories": ["imported", "external"],
            "tags": ["github"],
            "complexity": "unknown",
            "recommended_agents": [],
            "recommended_skills": []
        }
        
        with open(yaml_filepath, "w", encoding="utf-8") as f:
            yaml.dump(metadata, f, default_flow_style=False)
            
        print(f"Successfully imported {name} to {output_dir}")
        
    except Exception as e:
        print(f"Failed to import prompt from {url}. Error: {e}")

if __name__ == "__main__":
    # Example usage:
    # import_github_prompt("https://raw.githubusercontent.com/fabled-ray/awesome-prompts/main/prompts/developer.md", "Imported Developer")
    print("GitHub Prompts Importer Ready.")

import json
import os
import glob
import yaml
from typing import Dict, Any, List

class PromptAnalyzer:
    """
    Analyzes natural language requests to recommend prompts, agents, and skills based on the prompt library.
    Advanced version detects project type, language, complexity, specialists, and architectural patterns.
    """
    def __init__(self, prompts_dir: str = "C:/AI/Projects/AI-Agent-OS/omni_library/prompts"):
        self.prompts_dir = prompts_dir
        self.prompts_metadata = self._load_prompt_metadata()

    def _load_prompt_metadata(self) -> List[Dict[str, Any]]:
        metadata_list = []
        if os.path.exists(self.prompts_dir):
            for file_path in glob.glob(os.path.join(self.prompts_dir, "*_metadata.yaml")):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        data["_filename"] = os.path.basename(file_path).replace("_metadata.yaml", ".md")
                        metadata_list.append(data)
                except Exception as e:
                    pass
        return metadata_list

    def analyze(self, request: str) -> Dict[str, Any]:
        """
        Input: Natural language user request.
        Output: JSON with advanced extraction and scored prompts.
        """
        request_lower = request.lower()
        
        # Extended fields
        project_type = "general"
        programming_language = "unspecified"
        complexity = "low"
        architecture_pattern = "monolith"
        
        agents = set()
        skills = set()
        scored_prompts = []
        
        # Advanced heuristic extraction
        # Mobile Game
        if "mobile game" in request_lower or "game" in request_lower:
            project_type = "mobile_game"
            programming_language = "C#/C++"
            complexity = "high"
            architecture_pattern = "game_loop/ecs"
            agents.update(["GameDeveloper", "GraphicsProgrammer", "QA"])
            skills.update(["game_design", "rendering"])
            
        # SaaS Platform
        elif "saas" in request_lower or "platform" in request_lower:
            project_type = "saas_platform"
            programming_language = "TypeScript/Python"
            complexity = "high"
            architecture_pattern = "microservices"
            agents.update(["CTO", "Architect", "Backend", "Frontend", "QA"])
            skills.update(["architecture", "coding", "testing"])
            
        # Scientific Simulation
        elif "scientific" in request_lower or "simulation" in request_lower:
            project_type = "scientific_simulation"
            programming_language = "Python/C++"
            complexity = "high"
            architecture_pattern = "data_pipeline/hpc"
            agents.update(["DataScientist", "SimulationEngineer", "Backend"])
            skills.update(["mathematics", "performance_optimization"])

        # Replace heuristic prompt matching with Semantic RAG Retrieval
        from src.rag.prompt_indexer import PromptIndexer
        from src.rag.prompt_retriever import PromptRetriever
        
        # Build index (In production this would run separately on a schedule or on install)
        indexer = PromptIndexer()
        indexer.build_index()
        
        retriever = PromptRetriever(indexer)
        retrieved = retriever.retrieve(request_lower, top_k=3)
        
        for item in retrieved:
            scored_prompts.append({
                "name": item["name"] if "name" in item else item.get("metadata", {}).get("name", item["id"]),
                "relevance_score": round(item.get("score", 0.0), 2),
                "confidence_score": round(item.get("final_score", 0.0), 2)
            })
            
            meta = item.get("metadata", {})
            for agent in meta.get("recommended_agents", []):
                agents.add(agent)
            for skill in meta.get("recommended_skills", []):
                skills.add(skill)
                    
        return {
            "project_type": project_type,
            "programming_language": programming_language,
            "complexity": complexity,
            "architecture_pattern": architecture_pattern,
            "required_specialists": list(agents),
            "skills": list(skills),
            "prompts": scored_prompts
        }

import os
import yaml
import json
from src.rag.prompt_embedder import PromptEmbedder

class PromptIndexer:
    """
    Scans the prompt libraries and prepares them for semantic retrieval.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.base_path = base_path
        self.prompts_dir = os.path.join(base_path, "omni_library", "prompts")
        self.embedder = PromptEmbedder()
        self.index = [] # In-memory store for fallback mode
        
        # If we had Chroma, we'd initialize the collection here.
        self.has_chroma = self.embedder.has_chroma
        if self.has_chroma:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=os.path.join(base_path, "omni_library", "chroma_db"))
            self.collection = self.chroma_client.get_or_create_collection(name="omni_prompts")
            
    def build_index(self):
        """Scans the directories and builds the vector/fallback index."""
        if not os.path.exists(self.prompts_dir):
            return

        documents = []
        metadatas = []
        ids = []

        for root, _, files in os.walk(self.prompts_dir):
            for file in files:
                if file.endswith("_metadata.yaml"):
                    prompt_id = file.replace("_metadata.yaml", "")
                    meta_path = os.path.join(root, file)
                    
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = yaml.safe_load(f) or {}
                        
                    # Build search document
                    name = meta.get("name", prompt_id)
                    desc = meta.get("description", "")
                    tags = " ".join(meta.get("tags", []))
                    
                    content_to_embed = f"{name} {desc} {tags}"
                    
                    # Store in fallback
                    if not self.has_chroma:
                        self.index.append({
                            "id": prompt_id,
                            "name": name,
                            "metadata": meta,
                            "embedding": self.embedder.embed([content_to_embed])[0],
                            "raw_text": content_to_embed
                        })
                    else:
                        documents.append(content_to_embed)
                        clean_meta = {k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool))}
                        metadatas.append(clean_meta)
                        ids.append(prompt_id)

        if self.has_chroma and documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
    def close(self):
        """
        Releases file locks held by the ChromaDB PersistentClient.
        Essential for avoiding WinError 32 on Windows when cleaning up.
        """
        if hasattr(self, 'chroma_client'):
            try:
                import chromadb.api.client
                if hasattr(chromadb.api.client, "SharedSystemClient"):
                    chromadb.api.client.SharedSystemClient.clear_system_cache()
            except Exception as e:
                pass


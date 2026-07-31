"""Vector Store Interface for RAG Memory

Provides the Knowledge tier for agents.
"""

from typing import List, Dict, Any, Optional
import math

class Document:
    def __init__(self, id: str, content: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}

class InMemoryVectorStore:
    """A lightweight in-memory vector store using cosine similarity."""
    
    def __init__(self):
        self.documents: List[Document] = []
        
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
        
    def add_document(self, doc_id: str, content: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a document with its pre-computed embedding to the store."""
        self.documents.append(Document(id=doc_id, content=content, embedding=embedding, metadata=metadata))
        
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """Search the vector store for the closest embeddings."""
        scored_docs = []
        for doc in self.documents:
            score = self._cosine_similarity(query_embedding, doc.embedding)
            scored_docs.append((score, doc))
            
        # Sort descending by score
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scored_docs[:top_k]:
            results.append({
                "id": doc.id,
                "content": doc.content,
                "score": score,
                "metadata": doc.metadata
            })
            
        return results

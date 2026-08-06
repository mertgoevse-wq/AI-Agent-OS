import math
from src.rag.prompt_embedder import PromptEmbedder
from src.rag.prompt_ranker import PromptRanker

class PromptRetriever:
    """
    Handles retrieving prompts for a given query via vector search.
    """
    def __init__(self, indexer):
        self.indexer = indexer
        self.embedder = indexer.embedder
        self.ranker = PromptRanker()
        
    def retrieve(self, query: str, top_k: int = 5) -> list:
        """
        Retrieves and ranks prompts for a query.
        """
        if self.indexer.has_chroma:
            return self._retrieve_chroma(query, top_k)
        else:
            return self._retrieve_mock(query, top_k)
            
    def _retrieve_chroma(self, query: str, top_k: int) -> list:
        if self.indexer.collection.count() == 0:
            return []
            
        results = self.indexer.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.indexer.collection.count())
        )
        
        retrieved = []
        # Format results for the ranker
        for i in range(len(results['ids'][0])):
            retrieved.append({
                "id": results['ids'][0][i],
                "metadata": results['metadatas'][0][i],
                # Chroma returns distances (lower is better). Convert to a 0-1 similarity score roughly.
                "score": max(0.0, 1.0 - results['distances'][0][i])
            })
            
        return self.ranker.rank(retrieved)
        
    def _retrieve_mock(self, query: str, top_k: int) -> list:
        query_embedding = self.embedder.embed([query])[0]
        
        retrieved = []
        for doc in self.indexer.index:
            doc_emb = doc["embedding"]
            # Compute a fake cosine similarity between TF dictionaries
            intersection = set(query_embedding.keys()) & set(doc_emb.keys())
            
            numerator = sum(query_embedding[w] * doc_emb[w] for w in intersection)
            sum1 = sum(v**2 for v in query_embedding.values())
            sum2 = sum(v**2 for v in doc_emb.values())
            denominator = math.sqrt(sum1) * math.sqrt(sum2)
            
            sim_score = (numerator / denominator) if denominator else 0.0
            
            retrieved.append({
                "id": doc["id"],
                "metadata": doc["metadata"],
                "score": sim_score
            })
            
        ranked = self.ranker.rank(retrieved)
        return ranked[:top_k]

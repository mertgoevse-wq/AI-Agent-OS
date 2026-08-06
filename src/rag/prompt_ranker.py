class PromptRanker:
    """
    Ranks prompts retrieved from the vector store based on business logic.
    For example, official system prompts score higher than user imported ones,
    or we multiply the semantic score by the marketplace confidence_score.
    """
    def rank(self, retrieved_prompts: list) -> list:
        """
        Expects a list of dicts: {"id": str, "metadata": dict, "score": float}
        """
        for item in retrieved_prompts:
            meta = item.get("metadata", {})
            semantic_score = item.get("score", 0.0)
            
            # Base logic: Use marketplace confidence score if available
            confidence = float(meta.get("confidence_score", 0.5))
            
            # Boost official or highly used prompts
            source = meta.get("source", "unknown").lower()
            if "official" in source or "core" in source:
                confidence += 0.2
                
            # Final ranking score is a mix of semantic similarity and confidence
            item["final_score"] = (semantic_score * 0.7) + (confidence * 0.3)
            
        # Sort descending by final score
        return sorted(retrieved_prompts, key=lambda x: x.get("final_score", 0), reverse=True)

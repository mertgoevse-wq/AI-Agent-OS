import collections
import re
import math

class PromptEmbedder:
    """
    Handles generating embeddings for prompts.
    Falls back to a basic TF-IDF term-frequency model if chromadb isn't available.
    """
    def __init__(self):
        try:
            import chromadb
            import chromadb.utils.embedding_functions as embedding_functions
            self.has_chroma = True
            # In a real setup, we might use OpenAI or SentenceTransformers.
            # Here we default to the built-in Chroma MiniLM for simplicity if chroma is available.
            self.ef = embedding_functions.DefaultEmbeddingFunction()
        except ImportError:
            self.has_chroma = False

    def embed(self, texts: list[str]) -> list:
        if self.has_chroma:
            return self.ef(texts)
        else:
            # Fallback mock embedding (TF-IDF bag of words style representation)
            # This is solely to keep tests passing without requiring huge binary packages.
            return [self._mock_embed(t) for t in texts]
            
    def _mock_embed(self, text: str) -> dict:
        """
        A naive TF representation returned as a dict. 
        The retriever will know how to compare these mock 'embeddings'.
        """
        words = re.findall(r'\w+', text.lower())
        counter = collections.Counter(words)
        total = sum(counter.values()) if counter else 1
        return {word: count/total for word, count in counter.items()}

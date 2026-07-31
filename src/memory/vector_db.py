"""Vector Database Interface and Reference Implementation for AI-Agent-OS.

Defines the abstract VectorStore adapter and an offline InMemoryVectorStore
with Cosine similarity search and metadata filtering.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.memory.base import MemoryItem


class VectorRecord(BaseModel):
    """Vector embedding record stored in the vector database."""

    id: str
    vector: List[float]
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VectorSearchResult(BaseModel):
    """Result of a vector similarity search."""

    record: VectorRecord
    score: float  # Cosine similarity score (0.0 to 1.0)


class VectorStore(ABC):
    """Abstract interface for Vector Database adapters (e.g. Chroma, Qdrant, PGVector)."""

    @abstractmethod
    async def add(self, records: List[VectorRecord]) -> None:
        """Add vector records to the store."""
        ...

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Perform similarity search for a query vector."""
        ...

    @abstractmethod
    async def delete(self, record_ids: List[str]) -> None:
        """Delete records by ID."""
        ...

    @abstractmethod
    async def clear(self) -> None:
        """Clear all records from the store."""
        ...


class InMemoryVectorStore(VectorStore):
    """In-memory VectorStore implementation for testability and local execution without external DBs."""

    def __init__(self) -> None:
        self._records: Dict[str, VectorRecord] = {}

    @classmethod
    def create_simple_embedding(cls, text: str, dim: int = 16) -> List[float]:
        """Generate a deterministic normalized pseudo-embedding vector for offline testing."""
        vec = [0.0] * dim
        for i, char in enumerate(text):
            vec[i % dim] += ord(char)
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    @classmethod
    def cosine_similarity(cls, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity between two float vectors."""
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    async def add(self, records: List[VectorRecord]) -> None:
        """Add vector records to the in-memory database."""
        for record in records:
            self._records[record.id] = record

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Perform cosine similarity search with optional metadata filtering."""
        results: List[VectorSearchResult] = []

        for record in self._records.values():
            # Check metadata filter if supplied
            if metadata_filter:
                match = True
                for k, v in metadata_filter.items():
                    if record.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            score = self.cosine_similarity(query_vector, record.vector)
            results.append(VectorSearchResult(record=record, score=score))

        # Sort descending by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    async def delete(self, record_ids: List[str]) -> None:
        """Delete records by ID."""
        for rid in record_ids:
            self._records.pop(rid, None)

    async def clear(self) -> None:
        """Clear all records."""
        self._records.clear()

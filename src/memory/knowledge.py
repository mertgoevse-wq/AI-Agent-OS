"""Knowledge Memory for AI-Agent-OS.

Manages external reference documents, RAG chunks, and domain knowledge bases.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.memory.base import BaseMemory, MemoryItem


class DocumentChunk(MemoryItem):
    """Represents a chunk of a document for RAG indexing."""

    doc_id: str = ""
    chunk_index: int = 0


class KnowledgeMemory(BaseMemory):
    """Knowledge memory store for indexing and retrieving document context."""

    def __init__(self) -> None:
        self._chunks: Dict[str, MemoryItem] = {}

    async def store(self, item: MemoryItem) -> None:
        """Store a document chunk in knowledge memory."""
        if not item.timestamp:
            item.timestamp = time.time()
        self._chunks[item.id] = item

    async def add_document(self, doc_id: str, content: str, chunk_size: int = 500, metadata: Optional[Dict[str, Any]] = None) -> List[MemoryItem]:
        """Split a document into chunks and store each chunk."""
        words = content.split()
        chunks: List[MemoryItem] = []
        meta = metadata or {}

        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i : i + chunk_size])
            chunk_id = f"{doc_id}_chunk_{i // chunk_size}"
            item = MemoryItem(
                id=chunk_id,
                content=chunk_text,
                metadata={
                    "doc_id": doc_id,
                    "chunk_index": i // chunk_size,
                    **meta,
                },
                timestamp=time.time(),
            )
            await self.store(item)
            chunks.append(item)

        return chunks

    async def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Retrieve document chunks matching query keywords."""
        if not query:
            return list(self._chunks.values())[:limit]
        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        
        scored: List[tuple[int, MemoryItem]] = []
        for item in self._chunks.values():
            content_lower = item.content.lower()
            score = sum(1 for term in query_terms if term in content_lower)
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]

    async def clear(self) -> None:
        """Clear all stored document chunks."""
        self._chunks.clear()

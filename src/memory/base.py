"""Base memory interface for AI-Agent-OS."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """A generic record stored within a memory tier."""

    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = 0.0


class BaseMemory(ABC):
    """Abstract interface for all memory modules in AI-Agent-OS."""

    @abstractmethod
    async def store(self, item: MemoryItem) -> None:
        """Store a memory item."""
        ...

    @abstractmethod
    async def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Retrieve memory items matching a query."""
        ...

    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored memory items."""
        ...

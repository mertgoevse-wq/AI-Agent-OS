"""Long-Term Memory (LTM) for AI-Agent-OS.

Stores persistent user preferences, persona state, and agent reflection logs across sessions.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.memory.base import BaseMemory, MemoryItem


class LongTermMemory(BaseMemory):
    """Persistent key-value and reflection memory store."""

    def __init__(self) -> None:
        self._store: Dict[str, MemoryItem] = {}

    async def store(self, item: MemoryItem) -> None:
        """Store or update a long-term memory item."""
        if not item.timestamp:
            item.timestamp = time.time()
        self._store[item.id] = item

    async def set(self, key: str, value: Any, category: str = "general") -> MemoryItem:
        """Convenience method to set a key-value pair."""
        content = str(value) if not isinstance(value, str) else value
        item = MemoryItem(
            id=key,
            content=content,
            metadata={"key": key, "category": category, "raw_value": value},
            timestamp=time.time(),
        )
        await self.store(item)
        return item

    async def get(self, key: str, default: Any = None) -> Any:
        """Retrieve the raw value of a stored key."""
        item = self._store.get(key)
        if not item:
            return default
        return item.metadata.get("raw_value", item.content)

    async def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Retrieve memory items by key or content matching."""
        if not query:
            return list(self._store.values())[:limit]
        query_lower = query.lower()
        results = [
            item
            for item in self._store.values()
            if query_lower in item.id.lower() or query_lower in item.content.lower()
        ]
        return results[:limit]

    async def delete(self, key: str) -> bool:
        """Delete a memory item by key."""
        return self._store.pop(key, None) is not None

    async def clear(self) -> None:
        """Clear all long-term memory records."""
        self._store.clear()

"""Short-Term Memory (STM) for AI-Agent-OS.

Manages conversational turn buffer, sliding window context, and active task scratchpad.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.memory.base import BaseMemory, MemoryItem


class ShortTermMemory(BaseMemory):
    """Short-term memory with sliding window turn capacity."""

    def __init__(self, max_turns: int = 20) -> None:
        self.max_turns = max_turns
        self._history: List[MemoryItem] = []
        self._scratchpad: Dict[str, Any] = {}

    async def store(self, item: MemoryItem) -> None:
        """Store a conversation turn or message."""
        if not item.timestamp:
            item.timestamp = time.time()
        self._history.append(item)
        if len(self._history) > self.max_turns:
            self._history.pop(0)

    async def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> MemoryItem:
        """Convenience method to store a message by role."""
        item = MemoryItem(
            id=str(uuid4()),
            content=content,
            metadata={"role": role, **(metadata or {})},
            timestamp=time.time(),
        )
        await self.store(item)
        return item

    async def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Retrieve recent conversation items matching a query substring."""
        if not query:
            return self._history[-limit:]
        query_lower = query.lower()
        matching = [item for item in self._history if query_lower in item.content.lower()]
        return matching[-limit:]

    def get_context_window(self, max_turns: Optional[int] = None) -> List[Dict[str, str]]:
        """Format history as standard LLM message dicts [{'role': 'user', 'content': '...'}]"""
        count = max_turns or self.max_turns
        slice_items = self._history[-count:]
        return [
            {
                "role": item.metadata.get("role", "user"),
                "content": item.content,
            }
            for item in slice_items
        ]

    def set_scratchpad_value(self, key: str, value: Any) -> None:
        """Store a transient key-value pair in the active scratchpad."""
        self._scratchpad[key] = value

    def get_scratchpad_value(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the active scratchpad."""
        return self._scratchpad.get(key, default)

    async def clear(self) -> None:
        """Clear all conversation history and scratchpad data."""
        self._history.clear()
        self._scratchpad.clear()

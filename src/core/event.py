"""Event system for AI-Agent-OS.

Implements an async Pub/Sub Event Bus pattern.
"""

from __future__ import annotations

import asyncio
import fnmatch
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from src.schemas.common import EventType


class Event(BaseModel):
    """A system event that flows through the Event Bus."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)


# Type alias for async event handlers
EventHandler = Callable[[Event], Coroutine[Any, Any, None]]



class EventBus:
    """Async Pub/Sub Event Bus.

    Agents and system components can subscribe to specific event types
    or wildcard topics (e.g. 'agent.*', '*') and react to them asynchronously.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, Set[EventHandler]] = {}
        self._history: List[Event] = []
        self._lock = asyncio.Lock()

    def subscribe(
        self,
        event_type: Union[EventType, str],
        handler: EventHandler,
    ) -> None:
        """Register an async handler for a specific event type or wildcard pattern."""
        key = event_type.value if isinstance(event_type, EventType) else str(event_type)
        if key not in self._subscribers:
            self._subscribers[key] = set()
        self._subscribers[key].add(handler)

    def unsubscribe(
        self,
        event_type: Union[EventType, str],
        handler: EventHandler,
    ) -> None:
        """Remove a previously registered handler."""
        key = event_type.value if isinstance(event_type, EventType) else str(event_type)
        if key in self._subscribers:
            self._subscribers[key].discard(handler)

    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribed handlers matching the event type or pattern.

        All handlers are awaited concurrently and failures are collected
        so that one failing handler does not block others.
        """
        async with self._lock:
            self._history.append(event)

        event_str = event.type.value if isinstance(event.type, EventType) else str(event.type)
        matching_handlers: Set[EventHandler] = set()

        for pattern, handlers in self._subscribers.items():
            if pattern == "*" or pattern == event_str or fnmatch.fnmatch(event_str, pattern):
                matching_handlers.update(handlers)

        if not matching_handlers:
            return

        tasks = [handler(event) for handler in matching_handlers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log exceptions from handlers without disrupting the bus
        for result in results:
            if isinstance(result, Exception):
                import logging
                logging.getLogger(__name__).error(
                    "Event handler failed: %s", result
                )

    async def get_history(
        self,
        event_type: Optional[Union[EventType, str]] = None,
        limit: int = 100,
    ) -> List[Event]:
        """Retrieve recent event history, optionally filtered by type."""
        async with self._lock:
            if event_type is None:
                return self._history[-limit:]
            target = event_type.value if isinstance(event_type, EventType) else str(event_type)
            return [e for e in self._history[-limit:] if (e.type.value if isinstance(e.type, EventType) else str(e.type)) == target]

    def clear_history(self) -> None:
        """Clear all stored event history."""
        self._history.clear()
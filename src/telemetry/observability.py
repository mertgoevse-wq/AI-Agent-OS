"""Telemetry and observability module for AI-Agent-OS.

Prepares the system for distributed tracing and detailed metrics.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.core.event import Event, EventBus
from src.schemas.common import EventType

logger = logging.getLogger(__name__)


class Span:
    """A lightweight representation of a tracing span."""

    def __init__(self, name: str, parent_id: Optional[str] = None):
        import uuid
        self.id = str(uuid.uuid4())
        self.parent_id = parent_id
        self.name = name
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.attributes: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        self.events.append({
            "name": name,
            "timestamp": datetime.utcnow().isoformat(),
            "attributes": attributes or {}
        })

    def end(self) -> None:
        self.end_time = datetime.utcnow()


class TelemetryTracer:
    """Listens to the EventBus and generates structured telemetry data."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._active_spans: Dict[str, Span] = {}
        self._completed_spans: List[Span] = []
        
        # Subscribe to lifecycle events to generate spans
        self._event_bus.subscribe(EventType.TASK_CREATED, self._on_task_created)
        self._event_bus.subscribe(EventType.TASK_COMPLETED, self._on_task_completed)
        self._event_bus.subscribe(EventType.TASK_FAILED, self._on_task_failed)

    async def _on_task_created(self, event: Event) -> None:
        task_id = event.data.get("task_id")
        if task_id:
            span = Span(name=f"task_{task_id}")
            span.set_attribute("type", event.data.get("type", "unknown"))
            self._active_spans[task_id] = span
            logger.debug("[Telemetry] Started span for task %s", task_id)

    async def _on_task_completed(self, event: Event) -> None:
        task_id = event.data.get("task_id")
        span = self._active_spans.pop(task_id, None)
        if span:
            span.set_attribute("status", "completed")
            span.set_attribute("agent_id", event.data.get("agent_id"))
            span.end()
            self._completed_spans.append(span)
            logger.debug("[Telemetry] Completed span for task %s in %s", task_id, span.end_time - span.start_time)

    async def _on_task_failed(self, event: Event) -> None:
        task_id = event.data.get("task_id")
        span = self._active_spans.pop(task_id, None)
        if span:
            span.set_attribute("status", "failed")
            span.set_attribute("error", event.data.get("error"))
            span.end()
            self._completed_spans.append(span)
            logger.debug("[Telemetry] Failed span for task %s", task_id)

    def get_completed_spans(self) -> List[Span]:
        """Return the list of completed tracing spans."""
        return list(self._completed_spans)

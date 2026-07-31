"""Tests for expanded Event System and wildcard subscriptions."""

import pytest
from src.core.event import Event, EventBus
from src.schemas.common import EventType


@pytest.mark.asyncio
async def test_event_bus_wildcard_subscription():
    bus = EventBus()
    received_agent_events = []
    received_all_events = []

    async def handle_agent_events(event: Event):
        received_agent_events.append(event)

    async def handle_all_events(event: Event):
        received_all_events.append(event)

    # Subscribe wildcard topics
    bus.subscribe("agent.*", handle_agent_events)
    bus.subscribe("*", handle_all_events)

    # Publish events
    event_start = Event(type=EventType.AGENT_STARTED, source="agent_1", data={"info": "started"})
    event_tool = Event(type=EventType.TOOL_EXECUTING, source="agent_1", data={"tool": "search"})

    await bus.publish(event_start)
    await bus.publish(event_tool)

    # Verify matching
    assert len(received_agent_events) == 1
    assert received_agent_events[0].type == EventType.AGENT_STARTED

    assert len(received_all_events) == 2


@pytest.mark.asyncio
async def test_event_bus_new_event_types():
    bus = EventBus()
    events = []

    async def handler(event: Event):
        events.append(event)

    bus.subscribe(EventType.MODEL_FALLBACK_TRIGGERED, handler)
    bus.subscribe(EventType.TOOL_PERMISSION_DENIED, handler)

    e1 = Event(type=EventType.MODEL_FALLBACK_TRIGGERED, source="router", data={"from": "gpt-4o", "to": "claude"})
    e2 = Event(type=EventType.TOOL_PERMISSION_DENIED, source="agent_2", data={"tool": "delete_db"})

    await bus.publish(e1)
    await bus.publish(e2)

    assert len(events) == 2
    assert events[0].type == EventType.MODEL_FALLBACK_TRIGGERED
    assert events[1].type == EventType.TOOL_PERMISSION_DENIED

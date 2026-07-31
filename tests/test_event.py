"""Tests for the Event Bus system."""

import pytest
from src.core.event import Event, EventBus
from src.schemas.common import EventType


class TestEventCreation:
    """Test event creation."""

    def test_event_creates_with_defaults(self):
        event = Event(type=EventType.AGENT_STARTED)
        assert event.id is not None
        assert event.type == EventType.AGENT_STARTED
        assert event.timestamp is not None
        assert event.source == ""
        assert event.data == {}

    def test_event_with_custom_data(self):
        event = Event(
            type=EventType.TASK_CREATED,
            source="kernel",
            data={"task_id": "123"},
        )
        assert event.type == EventType.TASK_CREATED
        assert event.source == "kernel"
        assert event.data == {"task_id": "123"}

    def test_all_event_types_exist(self):
        """Verify all required event types are defined."""
        assert EventType.AGENT_STARTED == "agent.started"
        assert EventType.AGENT_STOPPED == "agent.stopped"
        assert EventType.TASK_CREATED == "task.created"
        assert EventType.TASK_COMPLETED == "task.completed"
        assert EventType.TASK_FAILED == "task.failed"
        assert EventType.AGENT_PAUSED == "agent.paused"
        assert EventType.AGENT_RESUMED == "agent.resumed"
        assert EventType.SKILL_LOADED == "skill.loaded"
        assert EventType.SKILL_UNLOADED == "skill.unloaded"


class TestEventBus:
    """Test the async Pub/Sub Event Bus."""

    @pytest.mark.asyncio
    async def test_publish_no_subscribers(self):
        """Publishing without subscribers should not raise."""
        bus = EventBus()
        event = Event(type=EventType.AGENT_STARTED)
        await bus.publish(event)  # Should not raise

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        """Subscribed handler should receive events."""
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.AGENT_STARTED, handler)
        event = Event(type=EventType.AGENT_STARTED, data={"msg": "hello"})
        await bus.publish(event)

        assert len(received) == 1
        assert received[0].data["msg"] == "hello"

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        """Multiple handlers for the same event type should all fire."""
        bus = EventBus()
        results = []

        async def handler1(event):
            results.append("h1")

        async def handler2(event):
            results.append("h2")

        bus.subscribe(EventType.TASK_CREATED, handler1)
        bus.subscribe(EventType.TASK_CREATED, handler2)
        await bus.publish(Event(type=EventType.TASK_CREATED))

        assert len(results) == 2
        assert "h1" in results
        assert "h2" in results

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Unsubscribed handlers should not receive events."""
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.AGENT_STARTED, handler)
        bus.unsubscribe(EventType.AGENT_STARTED, handler)
        await bus.publish(Event(type=EventType.AGENT_STARTED))

        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_selective_subscription(self):
        """Handlers should only receive events of their subscribed type."""
        bus = EventBus()
        agent_events = []
        task_events = []

        async def agent_handler(event):
            agent_events.append(event)

        async def task_handler(event):
            task_events.append(event)

        bus.subscribe(EventType.AGENT_STARTED, agent_handler)
        bus.subscribe(EventType.TASK_CREATED, task_handler)

        await bus.publish(Event(type=EventType.AGENT_STARTED))
        await bus.publish(Event(type=EventType.TASK_CREATED))

        assert len(agent_events) == 1
        assert len(task_events) == 1

    @pytest.mark.asyncio
    async def test_handler_exception_does_not_block(self):
        """A failing handler should not block other handlers."""
        bus = EventBus()
        results = []

        async def failing_handler(event):
            raise RuntimeError("Handler failed")

        async def good_handler(event):
            results.append("success")

        bus.subscribe(EventType.AGENT_STARTED, failing_handler)
        bus.subscribe(EventType.AGENT_STARTED, good_handler)

        await bus.publish(Event(type=EventType.AGENT_STARTED))

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_event_history(self):
        """Published events should be stored in history."""
        bus = EventBus()
        await bus.publish(Event(type=EventType.AGENT_STARTED, data={"id": "1"}))
        await bus.publish(Event(type=EventType.TASK_CREATED, data={"id": "2"}))
        await bus.publish(Event(type=EventType.AGENT_STOPPED, data={"id": "3"}))

        history = await bus.get_history()
        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_filtered_history(self):
        """History should be filterable by event type."""
        bus = EventBus()
        await bus.publish(Event(type=EventType.AGENT_STARTED))
        await bus.publish(Event(type=EventType.TASK_CREATED))

        filtered = await bus.get_history(event_type=EventType.AGENT_STARTED)
        assert len(filtered) == 1
        assert filtered[0].type == EventType.AGENT_STARTED

    @pytest.mark.asyncio
    async def test_clear_history(self):
        """History should be clearable."""
        bus = EventBus()
        await bus.publish(Event(type=EventType.AGENT_STARTED))
        bus.clear_history()
        history = await bus.get_history()
        assert len(history) == 0
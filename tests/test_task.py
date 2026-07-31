"""Tests for the Task model."""

import pytest
from datetime import datetime

from src.core.task import Task
from src.schemas.common import TaskStatus


class TestTaskCreation:
    """Test task creation and default values."""

    def test_task_creates_with_defaults(self):
        """A task should have sensible defaults."""
        task = Task(input="test input")
        assert task.id is not None
        assert task.type == "generic"
        assert task.input == "test input"
        assert task.status == TaskStatus.PENDING
        assert task.created_at is not None
        assert task.agent_id is None
        assert task.result is None
        assert task.error is None

    def test_task_with_custom_values(self):
        """A task should accept custom values."""
        task = Task(
            type="research",
            input="Search for X",
            agent_id="agent-1",
            metadata={"priority": "high"},
        )
        assert task.type == "research"
        assert task.input == "Search for X"
        assert task.agent_id == "agent-1"
        assert task.metadata == {"priority": "high"}

    def test_task_unique_ids(self):
        """Each task should have a unique ID."""
        task1 = Task(input="a")
        task2 = Task(input="b")
        assert task1.id != task2.id


class TestTaskTransitions:
    """Test task state transitions."""

    def test_pending_to_running(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        assert task.status == TaskStatus.RUNNING

    def test_running_to_completed(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        task.transition_to(TaskStatus.COMPLETED)
        assert task.status == TaskStatus.COMPLETED

    def test_running_to_failed(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        task.transition_to(TaskStatus.FAILED)
        assert task.status == TaskStatus.FAILED

    def test_running_to_waiting(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        task.transition_to(TaskStatus.WAITING)
        assert task.status == TaskStatus.WAITING

    def test_waiting_to_running(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        task.transition_to(TaskStatus.WAITING)
        task.transition_to(TaskStatus.RUNNING)
        assert task.status == TaskStatus.RUNNING

    def test_invalid_transition_raises_error(self):
        task = Task(input="test")
        with pytest.raises(ValueError, match="Invalid transition"):
            task.transition_to(TaskStatus.COMPLETED)  # Can't go PENDING -> COMPLETED

    def test_completed_cannot_transition(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        task.transition_to(TaskStatus.COMPLETED)
        with pytest.raises(ValueError):
            task.transition_to(TaskStatus.RUNNING)

    def test_failed_cannot_transition(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        task.transition_to(TaskStatus.FAILED)
        with pytest.raises(ValueError):
            task.transition_to(TaskStatus.RUNNING)


class TestTaskConvenienceMethods:
    """Test convenience methods on Task."""

    def test_assign_to(self):
        task = Task(input="test")
        task.assign_to("agent-42")
        assert task.agent_id == "agent-42"

    def test_complete(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        task.complete("done")
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "done"

    def test_fail(self):
        task = Task(input="test")
        task.transition_to(TaskStatus.RUNNING)
        task.fail("something went wrong")
        assert task.status == TaskStatus.FAILED
        assert task.error == "something went wrong"

    def test_updated_at_changes_on_transition(self):
        task = Task(input="test")
        original = task.updated_at
        task.transition_to(TaskStatus.RUNNING)
        assert task.updated_at >= original
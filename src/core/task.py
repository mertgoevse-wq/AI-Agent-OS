"""Task model for AI-Agent-OS."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.schemas.common import TaskStatus


class Task(BaseModel):
    """Represents a unit of work to be executed by an agent.

    A task flows through a lifecycle of states:
    PENDING → RUNNING → (COMPLETED | FAILED)
    It can also enter WAITING state (e.g. waiting for external input).
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str = "generic"
    input: str = ""
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    agent_id: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def transition_to(self, new_status: TaskStatus) -> None:
        """Transition the task to a new status with validation."""
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.RUNNING, TaskStatus.FAILED],
            TaskStatus.RUNNING: [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.WAITING],
            TaskStatus.WAITING: [TaskStatus.RUNNING, TaskStatus.FAILED],
            TaskStatus.COMPLETED: [],
            TaskStatus.FAILED: [],
        }

        allowed = valid_transitions.get(self.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition from {self.status.value} to {new_status.value}"
            )

        self.status = new_status
        self.updated_at = datetime.utcnow()

    def assign_to(self, agent_id: str) -> None:
        """Assign this task to an agent."""
        self.agent_id = agent_id
        self.updated_at = datetime.utcnow()

    def complete(self, result: str) -> None:
        """Mark the task as completed with a result."""
        self.transition_to(TaskStatus.COMPLETED)
        self.result = result
        self.updated_at = datetime.utcnow()

    def fail(self, error: str) -> None:
        """Mark the task as failed with an error message."""
        self.transition_to(TaskStatus.FAILED)
        self.error = error
        self.updated_at = datetime.utcnow()
"""Common schemas and type definitions for AI-Agent-OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
#  Enums
# ──────────────────────────────────────────────

class TaskStatus(str, Enum):
    """Possible states of a task throughout its lifecycle."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(str, Enum):
    """Possible states of an agent throughout its lifecycle."""

    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    TERMINATED = "terminated"


class EventType(str, Enum):
    """System event types for the event bus."""

    # Agent Events
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"
    AGENT_PAUSED = "agent.paused"
    AGENT_RESUMED = "agent.resumed"
    AGENT_STATE_CHANGED = "agent.state_changed"
    AGENT_ERROR = "agent.error"

    # Task Events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"

    # Skill Events
    SKILL_LOADED = "skill.loaded"
    SKILL_UNLOADED = "skill.unloaded"

    # Tool Events
    TOOL_REQUESTED = "tool.requested"
    TOOL_EXECUTING = "tool.executing"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"
    TOOL_PERMISSION_DENIED = "tool.permission_denied"

    # Model Events
    MODEL_REQUEST_STARTED = "model.request_started"
    MODEL_RESPONSE_RECEIVED = "model.response_received"
    MODEL_FALLBACK_TRIGGERED = "model.fallback_triggered"
    MODEL_BUDGET_EXCEEDED = "model.budget_exceeded"



# ──────────────────────────────────────────────
#  Pydantic Models
# ──────────────────────────────────────────────

class AgentCapability(BaseModel):
    """Declares a capability that an agent or skill provides."""

    name: str
    description: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    """Configuration for a model provider."""

    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str = "mock"
    options: Dict[str, Any] = Field(default_factory=dict)


class SkillManifest(BaseModel):
    """Schema for a skill.yaml manifest file."""

    name: str
    version: str = "0.1.0"
    description: str = ""
    capabilities: List[AgentCapability] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class TaskResult(BaseModel):
    """Result produced by executing a task."""

    task_id: str
    status: TaskStatus
    output: Optional[str] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionContext(BaseModel):
    """Context passed to an agent when executing a task."""

    task_id: str
    agent_id: str
    input: str
    skills: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    start_time: datetime = Field(default_factory=datetime.utcnow)
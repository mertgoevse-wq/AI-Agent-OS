from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class Event(BaseModel):
    """
    Ein generisches Event, das über den Event-Bus gesendet werden kann.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_agent_id: Optional[str] = None

class Task(BaseModel):
    """
    Eine Aufgabe, die einem Agenten zugewiesen wird.
    """
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Agent(ABC):
    """
    Basis-Klasse für alle Agenten im AI-Agent-OS.
    """
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.state = "idle" # idle, running, paused, terminated
        self.memory: List[Dict[str, Any]] = []
        
    @abstractmethod
    async def process_task(self, task: Task) -> Task:
        """
        Hauptmethode, die von Subklassen implementiert werden muss.
        Führt die eigentliche Arbeit des Agenten aus.
        """
        pass
        
    @abstractmethod
    def handle_event(self, event: Event) -> None:
        """
        Reagiert auf System-Events.
        """
        pass

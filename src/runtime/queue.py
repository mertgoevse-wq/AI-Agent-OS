"""Asynchronous task queue for Agent workload distribution."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional

from src.core.task import Task
from src.schemas.common import TaskStatus

logger = logging.getLogger(__name__)


class BaseTaskQueue(ABC):
    """Abstract interface for a task queue."""

    @abstractmethod
    async def enqueue(self, task: Task, priority: int = 0) -> None:
        """Add a task to the queue."""
        pass

    @abstractmethod
    async def dequeue(self) -> Task:
        """Remove and return the highest priority task."""
        pass
        
    @abstractmethod
    def qsize(self) -> int:
        """Return the approximate size of the queue."""
        pass


class InMemoryTaskQueue(BaseTaskQueue):
    """In-memory asyncio-based task queue."""

    def __init__(self) -> None:
        # PriorityQueue uses tuples (priority, count, task) to ensure stable sorting
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._counter = 0

    async def enqueue(self, task: Task, priority: int = 0) -> None:
        self._counter += 1
        # lower priority number = higher execution precedence
        await self._queue.put((priority, self._counter, task))
        logger.debug("Task %s enqueued with priority %s", task.id, priority)

    async def dequeue(self) -> Task:
        priority, _, task = await self._queue.get()
        logger.debug("Task %s dequeued (priority %s)", task.id, priority)
        return task

    def qsize(self) -> int:
        return self._queue.qsize()

    def task_done(self) -> None:
        self._queue.task_done()

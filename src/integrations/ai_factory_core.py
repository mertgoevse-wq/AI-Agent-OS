"""AI-Agent-OS adapter for the canonical AI Factory Core SDK.

Legacy AI-Agent-OS routers and registries remain available during migration;
new coding-runtime entry points should use this adapter instead.
"""

from __future__ import annotations

from pathlib import Path

from ai_factory_core import (
    CodingTaskRunner,
    DeveloperTools,
    FileSystemTools,
    ModelRouter,
    SQLiteTaskMemory,
)


def build_coding_runtime(root: str | Path, router: ModelRouter | None = None, database_path: str | Path | None = None) -> CodingTaskRunner:
    """Build a repository-scoped coding runner using central SDK components."""
    repository = Path(root).resolve()
    database = Path(database_path) if database_path else repository / ".ai-agent-os" / "tasks.sqlite3"
    database.parent.mkdir(parents=True, exist_ok=True)
    return CodingTaskRunner(
        router=router or ModelRouter(),
        root=repository,
        filesystem=FileSystemTools(repository),
        developer=DeveloperTools(repository),
        memory=SQLiteTaskMemory(database),
    )


__all__ = ["build_coding_runtime"]

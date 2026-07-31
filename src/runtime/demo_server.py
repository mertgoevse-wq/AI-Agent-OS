"""Demo REST API and Static File Web Server for AI-Agent-OS.

Provides an asynchronous HTTP backend powering the Claude Desktop-inspired UI Dashboard.
Serves static assets and exposes REST API endpoints for Agents, Skills, Models, Memory, and Workflows.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from src.core.event import Event, EventBus
from src.runtime.kernel import Kernel

from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory
from src.memory.knowledge import KnowledgeMemory
from src.memory.vector_db import InMemoryVectorStore, VectorRecord
from src.models.universal_router import TokenBudgetManager, UniversalModelRouter
from src.models.providers import (
    GoogleGeminiProvider,
    OpenAICompatibleProvider,
    AnthropicProvider,
    OllamaProvider,
    LocalRESTProvider,
    MockProvider,
)
from src.registry.agent_registry import AgentRegistry
from src.registry.skill_registry import SkillRegistry
from src.runtime.orchestrator import MultiAgentOrchestrator
from src.schemas.common import EventType

logger = logging.getLogger(__name__)


class DemoSystemState:
    """Singleton container for the live runtime state of AI-Agent-OS."""

    def __init__(self) -> None:
        self.event_bus = EventBus()
        self.budget_manager = TokenBudgetManager(max_daily_budget_usd=50.0)
        self.model_router = UniversalModelRouter(
            event_bus=self.event_bus,
            budget_manager=self.budget_manager,
        )

        # Register providers
        self.model_router.register_provider("mock", MockProvider())
        self.model_router.register_provider("google", GoogleGeminiProvider())
        self.model_router.register_provider("openai", OpenAICompatibleProvider())
        self.model_router.register_provider("anthropic", AnthropicProvider())
        self.model_router.register_provider("ollama", OllamaProvider())
        self.model_router.register_provider("local", LocalRESTProvider())

        self.active_provider = "mock"
        self.active_model = "mock"

        self.agent_registry = AgentRegistry()
        self.skill_registry = SkillRegistry()

        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        self.knowledge_mem = KnowledgeMemory()
        self.vector_store = InMemoryVectorStore()

        self.kernel = Kernel(
            agent_registry=self.agent_registry,
            skill_registry=self.skill_registry,
            model_router=self.model_router,
            event_bus=self.event_bus,
        )

        self.orchestrator = MultiAgentOrchestrator(
            agent_registry=self.agent_registry,
            event_bus=self.event_bus,
            model_router=self.model_router,
            stm=self.stm,
            ltm=self.ltm,
            knowledge_mem=self.knowledge_mem,
        )

        # Seed initial assets
        self.bootstrap()

    def bootstrap(self) -> None:
        """Scan Genesis_Harness and local workspace directories for agents & skills."""
        # 1. Scan Genesis_Harness if present
        genesis_path = Path(r"C:\Genesis_Harness")
        if genesis_path.exists():
            gen_agents = genesis_path / "agents"
            gen_skills = genesis_path / "skills"
            if gen_agents.exists():
                self.agent_registry._agents_dir = str(gen_agents)
                self.agent_registry.scan_agents_directory()
            if gen_skills.exists():
                self.skill_registry._skills_dir = str(gen_skills)
                self.skill_registry.scan_skills_directory()

        # 2. Scan local workspace
        self.agent_registry.scan_agents_directory()
        self.skill_registry.scan_skills_directory()

        # Seed sample memory items if empty
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._seed_sample_memory())
        except RuntimeError:
            asyncio.run(self._seed_sample_memory())


    async def _seed_sample_memory(self) -> None:
        """Pre-populate sample memory data for demonstration."""
        await self.stm.add_message("user", "System Initialized. Active theme: Calm Dark.")
        await self.ltm.set("platform_name", "AI-Agent-OS", category="system")
        await self.ltm.set("ui_theme", "Claude Desktop Dark", category="preference")
        await self.knowledge_mem.add_document(
            doc_id="ai_agent_os_architecture",
            content="AI-Agent-OS is a universal agent platform supporting Genesis_Harness skills, multi-provider model routing, 4-tier memory, and RBAC permissions.",
        )
        
        vec1 = InMemoryVectorStore.create_simple_embedding("AI-Agent-OS Universal Architecture", dim=8)
        vec2 = InMemoryVectorStore.create_simple_embedding("Genesis_Harness Skill & Agent Loader", dim=8)
        
        await self.vector_store.add([
            VectorRecord(id="v1", vector=vec1, content="AI-Agent-OS Universal Architecture", metadata={"tier": "knowledge"}),
            VectorRecord(id="v2", vector=vec2, content="Genesis_Harness Skill & Agent Loader", metadata={"tier": "skills"}),
        ])


# Global runtime instance
system_state = DemoSystemState()


class DemoHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP Handler serving static SPA dashboard files and REST API endpoints."""

    static_dir = Path(__file__).parent.parent / "ui" / "static"

    def translate_path(self, path: str) -> str:
        """Serve files from src/ui/static/."""
        parsed = urlparse(path)
        clean_path = parsed.path
        if clean_path == "/" or not clean_path:
            clean_path = "/index.html"
        target = self.static_dir / clean_path.lstrip("/")
        return str(target)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._handle_api_get(parsed.path, parse_qs(parsed.query))
        else:
            super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            payload = json.loads(post_body)
        except Exception:
            payload = {}

        if parsed.path.startswith("/api/"):
            self._handle_api_post(parsed.path, payload)
        else:
            self._send_json({"error": "Not Found"}, status=404)

    def _handle_api_get(self, path: str, params: Dict[str, List[str]]) -> None:
        if path == "/api/status":
            history = asyncio.run(system_state.event_bus.get_history(limit=50))
            data = {
                "status": "online",
                "kernel_running": system_state.kernel._running,
                "active_agents_count": system_state.agent_registry.count(),
                "loaded_skills_count": len(system_state.skill_registry.list_skills()),
                "total_cost_usd": round(system_state.budget_manager.total_cost_usd, 4),
                "max_daily_budget_usd": system_state.budget_manager.max_daily_budget_usd,
                "active_provider": system_state.active_provider,
                "active_model": system_state.active_model,
                "total_events_logged": len(history),
            }
            self._send_json(data)

        elif path == "/api/agents":
            agents_list = []
            for agent in system_state.agent_registry.list_agents():
                defn = system_state.agent_registry.get_definition(agent.id)
                agents_list.append({
                    "id": agent.id,
                    "name": agent.name,
                    "role": defn.role if defn else "assistant",
                    "description": agent.description,
                    "state": agent.state.value if hasattr(agent.state, "value") else str(agent.state),
                    "required_skills": defn.required_skills if defn else [],
                    "permissions": defn.permissions.dict() if defn else {},
                })
            self._send_json({"agents": agents_list})

        elif path == "/api/skills":
            skills_list = []
            for skill in system_state.skill_registry.list_skills():
                skills_list.append({
                    "name": skill.name,
                    "version": skill.version,
                    "description": skill.description,
                    "source_path": skill.source_path,
                    "dependencies": skill.manifest.dependencies,
                    "instructions": skill.extended.instructions if skill.extended else "",
                })
            self._send_json({"skills": skills_list})

        elif path == "/api/models":
            providers = system_state.model_router.list_providers()
            self._send_json({
                "providers": providers,
                "active_provider": system_state.active_provider,
                "active_model": system_state.active_model,
                "max_daily_budget_usd": system_state.budget_manager.max_daily_budget_usd,
                "total_cost_usd": round(system_state.budget_manager.total_cost_usd, 4),
            })

        elif path == "/api/memory":
            stm_window = system_state.stm.get_context_window()
            ltm_items = asyncio.run(system_state.ltm.retrieve("", limit=20))
            knowledge_items = asyncio.run(system_state.knowledge_mem.retrieve("", limit=20))
            
            # Simple vector search query if provided
            query = params.get("q", ["AI"])[0]
            query_vec = InMemoryVectorStore.create_simple_embedding(query, dim=8)
            vector_results = asyncio.run(system_state.vector_store.search(query_vec, limit=5))

            self._send_json({
                "short_term": stm_window,
                "long_term": [i.dict() for i in ltm_items],
                "knowledge": [i.dict() for i in knowledge_items],
                "vector_results": [
                    {
                        "id": r.record.id,
                        "content": r.record.content,
                        "score": round(r.score, 4),
                        "metadata": r.record.metadata,
                    }
                    for r in vector_results
                ],
            })

        elif path == "/api/events/history":
            history = asyncio.run(system_state.event_bus.get_history(limit=100))
            formatted = [
                {
                    "id": e.id,
                    "type": e.type.value if hasattr(e.type, "value") else str(e.type),
                    "timestamp": e.timestamp.isoformat() if hasattr(e.timestamp, "isoformat") else str(e.timestamp),
                    "source": e.source,
                    "data": e.data,
                }
                for e in history
            ]
            self._send_json({"events": formatted})

        else:
            self._send_json({"error": "Endpoint not found"}, status=404)

    def _handle_api_post(self, path: str, payload: Dict[str, Any]) -> None:
        if path == "/api/router/config":
            provider = payload.get("provider", "mock")
            model = payload.get("model", "mock")
            budget = payload.get("max_daily_budget_usd")

            if provider in system_state.model_router.list_providers():
                system_state.active_provider = provider
            if model:
                system_state.active_model = model
            if budget is not None:
                system_state.budget_manager.max_daily_budget_usd = float(budget)

            self._send_json({
                "status": "updated",
                "active_provider": system_state.active_provider,
                "active_model": system_state.active_model,
                "max_daily_budget_usd": system_state.budget_manager.max_daily_budget_usd,
            })

        elif path == "/api/workflow/execute":
            topic = payload.get("topic", "Analysiere KI-Agenten Trends 2026")
            model = payload.get("model", system_state.active_model)

            wf_result = asyncio.run(
                system_state.orchestrator.run_topic_analysis_workflow(
                    topic=topic,
                    model=model,
                )
            )

            self._send_json(wf_result.dict())

        elif path == "/api/tasks/execute":
            agent_id = payload.get("agent_id", "architect")
            task_input = payload.get("input", "Review system architecture")

            task = Task(input=task_input, agent_id=agent_id)
            result = asyncio.run(system_state.kernel.submit_task(task))

            self._send_json({
                "task_id": result.id,
                "status": result.status.value if hasattr(result.status, "value") else str(result.status),
                "output": result.output or f"Task processed for agent '{agent_id}'",
                "error": result.error,
            })


        else:
            self._send_json({"error": "Endpoint not found"}, status=404)

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default HTTP request logging for cleaner console."""
        pass

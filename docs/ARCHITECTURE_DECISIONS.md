# ARCHITECTURE DECISIONS (ADR) — AI-Agent-OS

**Document Version:** 1.0.0  
**Role:** Lead AI Systems Architect  
**Date:** 2026-07-31  

---

## Overview

This document records the foundational architectural decisions made for **AI-Agent-OS**, following the Architecture Decision Record (ADR) format.

---

## ADR-001: Unified Markdown + YAML Frontmatter Parser for Skills and Charters

### Status: APPROVED

### Context
The pre-existing Genesis_Harness framework defines agents and skills primarily in Markdown format (`SKILL.md` and `AGENT.md`) with YAML frontmatter headers. The initial Phase 1 of AI-Agent-OS only parsed simple `skill.yaml` files. To enable seamless compatibility without requiring duplicate asset maintenance or code generation, AI-Agent-OS must natively ingest both formats.

### Decision
Implement a unified loader using `python-frontmatter` / PyYAML fallback regex parsing. The parser extracts structured metadata (YAML header) and preserves markdown body content as executable prompt context for LLM agents.

### Consequences
- **Positive**: Direct 100% compatibility with ~50 Genesis_Harness agent charters and ~56 skill definitions.
- **Positive**: Non-developers can author agents and skills using plain Markdown.
- **Negative**: Requires robust error handling when frontmatter fields are malformed or missing.

---

## ADR-002: Dynamic Model Router with Provider Fallback Chains and Token Budgeting

### Status: APPROVED

### Context
Relying on a single LLM provider creates vendor lock-in, vulnerability to API downtime, rate limiting, and cost inefficiency. Downstream apps (CryptoPilot-AI, AirBeat Studio) have differing needs for latency, context size, and multimodal support.

### Decision
Build a provider-agnostic `ModelRouter` interface supporting 6 core backends:
1. Google Gemini
2. OpenAI Compatible APIs
3. Anthropic
4. OpenRouter
5. Ollama
6. Local / REST Endpoints

Include capability matching (e.g. `vision`, `function_calling`, `json_mode`), automatic fallback chains upon API errors (429/5xx), and a central token budget tracker.

### Consequences
- **Positive**: High availability and zero vendor lock-in.
- **Positive**: Cost optimization by automatically routing simple tasks to smaller models (`gpt-4o-mini`, `gemini-1.5-flash`).
- **Negative**: Standardizing message structures and parameter mappings across distinct API schemas adds slight adapter complexity.

---

## ADR-003: 4-Tier Memory System Architecture with Pluggable Vector DB Adapter

### Status: APPROVED

### Context
Agents need distinct memory horizons: immediate task scratchpads, user state over time, reference documentation, and high-dimensional semantic search.

### Decision
Establish a clear 4-tier memory architecture:
1. **Short-Term Memory (STM)**: Turn buffer and sliding window.
2. **Long-Term Memory (LTM)**: Key-value user and agent state persistence.
3. **Knowledge Memory**: RAG document store.
4. **Vector Database Interface**: Abstract `VectorStore` adapter supporting vector embedding generation, Cosine similarity search, metadata filtering, and an in-memory reference implementation for testing without external services.

### Consequences
- **Positive**: Clear separation of concerns; easy to swap in Chroma, Qdrant, or PGVector later.
- **Positive**: Enables fully offline, zero-dependency testing using the in-memory vector store.

---

## ADR-004: Granular 3-Tier Event System (Agent, Task, Tool, Model)

### Status: APPROVED

### Context
Phase 1 established a simple 9-event `EventType` enum. As the platform grows to support multi-agent orchestration, complex tool sandboxing, and telemetry, event types must be systematically organized.

### Decision
Extend `EventType` and `EventBus` to categorize events into 4 primary domains:
- `agent.*`: Started, Stopped, Paused, Resumed, StateChanged, Error.
- `task.*`: Created, Started, Progress, Completed, Failed, Cancelled.
- `tool.*`: Requested, Executing, Completed, Failed, PermissionDenied.
- `model.*`: RequestStarted, ResponseReceived, FallbackTriggered, BudgetExceeded.

### Consequences
- **Positive**: Subsystems can subscribe to domain wildcards (e.g., all `tool.*` events for auditing).
- **Positive**: Enables complete execution observability and tracing.

---

## ADR-005: Declarative Role & Attribute-Based Access Control (RBAC/ABAC)

### Status: APPROVED

### Context
Agents executing tools (especially in financial plugins like CryptoPilot-AI or system plugins writing files) require explicit security boundaries to prevent prompt injection or unintended actions.

### Decision
Implement declarative permission policies on both Agent Definitions and Skill Manifests. Tool executions evaluate:
1. Is the agent granted the required tool role/permission?
2. Are input parameters within authorized bounds (e.g. file paths within workspace, budget limit)?

Defaults strictly to **DENY** if unspecified.

### Consequences
- **Positive**: Enterprise-grade security for downstream plugins.
- **Negative**: Unconfigured test agents will fail tool execution unless granted explicit permissions.

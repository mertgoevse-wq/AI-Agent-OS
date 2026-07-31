# AI-Agent-OS — Universal Autonomous Agent Platform

AI-Agent-OS is a universal, event-driven agent platform designed to host enterprise autonomous agent applications (e.g. **CryptoPilot-AI**, **AirBeat Studio**) and natively execute **Genesis_Harness** agent charters (`AGENT.md`) and domain skills (`SKILL.md`).

---

## Key Platform Features

- **Genesis_Harness Native Compatibility**: Automatically loads and parses ~50 specialized agent definitions and ~56 domain skills written in Markdown with YAML frontmatter headers.
- **Universal Skill Loader**: Supports SemVer metadata, capability declarations, and topological dependency sorting (with circular dependency detection).
- **Agent Registry & Security Policies**: Declarative Role & Attribute-Based Access Control (RBAC/ABAC) specifying tool permissions (`READ_ONLY`, `FILE_WRITE`, `EXECUTE_CODE`, `NETWORK_ACCESS`, `ADMIN`).
- **Multi-Provider Model Router**: Provider abstraction supporting Google Gemini, OpenAI Compatible (vLLM, LocalAI), Anthropic Claude, OpenRouter, Ollama, and Local REST endpoints with capability matching, fallback chains, and token spend budgeting.
- **4-Tier Memory System Architecture**:
  - **Short-Term Memory (STM)**: Sliding window turn buffer, scratchpads, auto-truncation.
  - **Long-Term Memory (LTM)**: Key-value persistent state and agent reflection logs.
  - **Knowledge Memory**: RAG document chunking and indexing.
  - **Vector Database Interface**: Abstract adapter & `InMemoryVectorStore` reference implementation with Cosine similarity search and metadata filtering.
- **Multi-Agent Sequential & Graph Orchestration**: Built-in 4-agent topic analysis workflow (`Supervisor Agent` -> `Research Agent` -> `Verification Agent` -> `Report Agent`).
- **Next.js UI Dashboard**: Modern React-based frontend (`ui/`) with Workflow Studio, Agents/Skills directory, Memory inspector, and live system metrics.

---

## Quickstart & Launching the Demo

### Prerequisites
- Python 3.10+
- `pytest` (for running tests)

### 1. Run Unit Tests
Verify the full platform test suite (119 tests):
```powershell
pytest -v
```

### 2. Launch the Platform

**Backend (Python API Server):**
Start the asynchronous demo web server and kernel runtime:
```powershell
python demo.py
```
The API will run on `http://127.0.0.1:8000`.

**Frontend (Next.js Dashboard):**
Open a new terminal and start the Next.js development server:
```powershell
cd ui
npm run dev
```
Open your browser and navigate to:
```
http://localhost:3000
```

---

## System Architecture Overview

```
+-------------------------------------------------------------------+
|                        UI DASHBOARD (SPA)                         |
|   (Overview | Workflow Studio | Agents & Skills | Memory | Router)|
+---------------------------------|---------------------------------+
                                  | REST API / WebSockets
+---------------------------------v---------------------------------+
|                       AI-AGENT-OS KERNEL                          |
|                                                                   |
|   +-----------------------+           +-----------------------+   |
|   | Multi-Agent           |           |  Universal Skill      |   |
|   | Orchestrator          |           |  & Agent Registries   |   |
|   +-----------+-----------+           +-----------+-----------+   |
|               |                                   |               |
|   +-----------+-----------+           +-----------+-----------+   |
|   | 4-Tier Memory System  |           | Universal Model       |   |
|   | (STM/LTM/Knowledge/   |           | Router                |   |
|   | Vector DB)            |           | (Gemini/Claude/Mock)  |   |
|   +-----------+-----------+           +-----------+-----------+   |
|               |                                   |               |
|   +-----------+-----------------------------------+-----------+   |
|   |                 Async Event Bus (Pub/Sub)                 |   |
|   +-----------------------------------------------------------+   |
+-------------------------------------------------------------------+
```

---

## Project Documentation

Detailed architecture specifications are located in the `docs/` directory:
- [CURRENT_STATE.md](docs/CURRENT_STATE.md) — System state and gap analysis.
- [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) — Technical implementation specifications.
- [INTEGRATION_PLAN.md](docs/INTEGRATION_PLAN.md) — Downstream plugin integration guide.
- [ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md) — Architecture Decision Records (ADR-001 to ADR-005).

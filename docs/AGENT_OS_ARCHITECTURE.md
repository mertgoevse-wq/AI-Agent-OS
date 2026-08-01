# OMNI AGENT OS ARCHITECTURE
## Core Concept
The AI-Agent-OS is now structured as an **OMNI-Agent-Swarm**, grouping specialized agents into domain-specific swarms (Architecture, Engineering, AI, Automation, Quality, Product).

## Key Components
1. **Swarm Orchestrator**: Manages delegation across swarm subgroups (`src/core/swarm.py`).
2. **Supervisor Evaluator**: A quality gate that evaluates task outputs (`src/runtime/evaluator.py`).
3. **MCP Client**: Interacts with standard external tools seamlessly (`src/mcp/mcp_client.py`).
4. **Prompt Registry**: Context-aware versioning for LLM system prompts (`src/registry/prompt_registry.py`).

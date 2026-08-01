# Advanced Prompt Fusion Engine (Phase 3)

The Advanced Prompt Fusion Engine is designed to take the heuristic analysis from the `PromptAnalyzer` and dynamically generate a structured, highly robust `MASTER FUSED PROMPT` for the OMNI-Agent-OS orchestration layer.

## The Analyzer Enhancements
Before fusion can happen, the `PromptAnalyzer` extracts deep context from natural language, mapping requests to:
- **Project Type** (e.g., `mobile_game`, `saas_platform`, `scientific_simulation`)
- **Programming Language** (e.g., `C#/C++`, `TypeScript/Python`)
- **Complexity** (e.g., `low`, `high`)
- **Architecture Pattern** (e.g., `game_loop/ecs`, `microservices`)
- **Required Specialists** (e.g., `Backend`, `GameDeveloper`)

Additionally, all matching base prompts from the `omni_library` are returned with calculated scoring:
- `relevance_score` (0.0 to 1.0)
- `confidence_score` (0.0 to 1.0)

## The Fusion Layout
The `PromptFusionEngine.fuse(analysis_context)` method guarantees that the LLM is initialized with a strict framework. The fused prompt will always contain the following sections:

### 1. System Role
Defines the overarching directive of the ecosystem based on the exact `project_type`.

### 2. Agent Team
Explicitly lists the `required_specialists` so the swarm model knows exactly which personas it must simulate or delegate to.

### 3. Workflow
Injects the defined `architecture_pattern` and `complexity` to ground the model's architectural decisions (e.g., instructing the swarm to use a Microservices pattern instead of a Monolith).

### 4. Requirements
Defines the `programming_language` and general technical constraints.

### 5. Testing Strategy
Enforces test-driven methodologies (unit/integration) for all components.

### 6. Deployment Strategy
Enforces the creation of infrastructure-as-code or standard deployment manifests alongside application code.

### 7. Loaded Contexts
Appends the literal markdown contents of the matching base prompts (e.g., "SaaS Builder", "Full Stack Developer"), separated by clear delimiters and tagged with their `relevance_score`.

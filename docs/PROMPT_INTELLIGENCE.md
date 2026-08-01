# OMNI Prompt Intelligence Engine

The Prompt Intelligence Engine is the core subsystem of OMNI-Agent-OS responsible for dynamically mapping natural language user requests to highly specialized agent contexts, skills, and base prompts.

## Overview

The engine operates through three main components:
1. **Prompt Library System** (`omni_library/prompts/`)
2. **Prompt Analyzer** (`src/core/prompt_analyzer.py`)
3. **Prompt Fusion Engine** (`src/core/prompt_fusion.py`)

## 1. Prompt Library System

Prompts are stored as markdown files (`.md`) that contain the actual system instructions. Each prompt is accompanied by a metadata file (`_metadata.yaml`) that helps the system understand when to apply the prompt.

**Example `saas_builder_metadata.yaml`:**
```yaml
name: "SaaS Builder"
description: "Master prompt for building a complete SaaS application."
categories: ["software_development", "saas"]
tags: ["architecture", "fullstack", "startup"]
complexity: "high"
recommended_agents: ["CTO", "Architect", "Backend", "Frontend", "QA"]
recommended_skills: ["architecture", "coding", "testing"]
```

## 2. Prompt Analyzer

The `PromptAnalyzer` interprets the user's natural language input. It scans the `omni_library/prompts/` directory, extracts metadata, and performs heuristic matching against the text.

**Outputs:**
- `task_type`
- `domain`
- `complexity`
- `agents` (List of required agents for the task)
- `skills` (List of required skills)
- `prompts` (List of matching base prompts)

## 3. Prompt Fusion Engine

When the `PromptAnalyzer` identifies multiple relevant prompts (e.g., combining a "Frontend Developer" prompt with a "Security Architect" prompt), the `PromptFusionEngine` takes over.

It loads the underlying markdown content, wraps them in explicit delimiters (`--- BEGIN [Prompt Name] ---`), and fuses them into a single `MASTER FUSED PROMPT`. This guarantees that the LLM receives unified, conflict-resolved context spanning multiple specializations.

## 4. External Prompts (`scripts/import_github_prompts.py`)

To expand the intelligence engine, you can import prompts from external open-source repositories (like GitHub, zdoc).
The script automatically fetches raw markdown and scaffolds the required `metadata.yaml` for immediate integration into the engine.

Run it via:
```bash
python scripts/import_github_prompts.py
```

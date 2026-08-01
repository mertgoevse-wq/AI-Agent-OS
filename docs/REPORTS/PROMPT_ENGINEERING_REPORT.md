# Prompt Engineering Report
## Overview
Agents currently use a static prompt string defined in `AGENT.md`.
## OMNI Upgrade Path
- **Prompt Versioning:** Implement a Prompt Library system to version, A/B test, and hot-swap system prompts dynamically.
- **Context Injection:** The orchestrator must inject dynamic metadata (time, budget remaining, memory constraints) into the prompt safely.

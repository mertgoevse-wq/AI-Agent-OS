# PROMPT SYSTEM
## Overview
Located at `prompts/library.yaml` and loaded via `src/registry/prompt_registry.py`.

## Capabilities
- **Versioning:** Allows hot-swapping prompt versions.
- **Context Injection:** Injects time, budget, and memory constraints dynamically into the `{{context}}` placeholders inside prompt definitions.

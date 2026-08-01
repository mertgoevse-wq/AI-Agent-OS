# Tool Integration Report
## Overview
Tools are currently hardcoded Python functions mapped in the `SkillRegistry`.
## OMNI Upgrade Path
- **MCP Integration:** Bind the OS to the Model Context Protocol (MCP) to standardize external tool calling across Anthropic and Gemini natively.
- **Sandboxing:** Implement execution sandboxes (e.g., restricted containers) for external code execution tasks to protect the core OS.

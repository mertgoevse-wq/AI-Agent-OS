# AGENT MONITORING CONCEPT

The visual monitoring system for OMNI-Agent-OS will act as the control room for local swarms, integrating seamlessly with future UIs and the Claude Desktop integration.

## Dashboard Metrics

1. **Active Task**
   - **Status**: Display current task description, category, and state (e.g., Planning, Executing, Evaluating).
   - **Origin**: Show if task originated from a CLI script, API, or Claude Desktop MCP query.

2. **Active Agents**
   - **Roster**: List of agents currently assigned (e.g., `backend_engineer`, `system_architect`).
   - **Role**: Display the agent's defined role from the `omni_library`.

3. **Loaded Skills**
   - **Utilization**: Track which skills are currently bound to active agents (e.g., `code_analysis`, `architecture_design`).

4. **Model Auswahl (Selection)**
   - **Router Status**: Show which model (e.g., `claude-3-opus`, `gemini-1.5-flash`) was chosen by the `ModelRouter` and why (e.g., Tier `pro_high` requirement).

5. **Tool Calls**
   - **Execution Log**: Stream of MCP tool calls requested and executed in real-time, providing transparency into the exact commands and file reads.

6. **Ergebnisse (Results)**
   - **Artifacts**: Display outputs, JSON decisions, and modified files.

7. **Tests**
   - **Test Status**: Visual indication of unit test status (pass/fail) triggered by agents during their evaluation cycle.

## Future Implementation
This monitoring concept will be materialized as a React/Next.js dashboard querying the OMNI-Agent-OS state endpoints, or as an embedded webview in compatible MCP clients.

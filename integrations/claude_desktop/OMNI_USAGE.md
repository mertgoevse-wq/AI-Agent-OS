# OMNI-Agent-OS Usage with Claude Desktop

When OMNI-Agent-OS is connected to Claude Desktop via the MCP server, Claude acts as the interface, while OMNI acts as the execution engine.

## How Claude interacts with OMNI

1. **Loading Agents (`list_agents`, `select_agents_for_task`)**
   Claude Desktop will query the OMNI MCP server to list available agents from the `omni_library`. When the user requests a task, Claude will use `select_agents_for_task` to invoke the `MetaRouter` and get the best agent recommendations.

2. **Loading Skills (`list_skills`)**
   Once an agent is selected, Claude will query the available skills associated with that agent's role.

3. **Loading Prompts (`get_prompt_template`)**
   Claude retrieves structured system prompts and guidelines from the OMNI library to align its reasoning process with the local swarms.

4. **Project Context (`get_project_context`)**
   Before executing a task, Claude fetches the current context (e.g., `PROJECT_STATE.md`) via the MCP endpoint to avoid hallucinating the environment.

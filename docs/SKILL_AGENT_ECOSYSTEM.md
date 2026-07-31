# AI-Agent-OS: Skill & Agent Ecosystem

The AI-Agent-OS framework acts as a runtime kernel for executing specialized AI agents equipped with unique skills. As part of its universal design, the framework natively hooks into external ecosystem harnesses, enabling zero-configuration discovery and hot-loading of pre-configured agents and skills.

## Ecosystem Overview

The primary upstream source for capabilities is the **Genesis Harness**.

- **Agents Source Directory:** `C:\Genesis_Harness\agents`
- **Skills Source Directory:** `C:\Genesis_Harness\skills`

The ecosystem currently comprises **53 distinct Agent roles** and **56 broad Skill domains**.

### Agent Categories (Overview)
Agents define specific personas, instructions, capabilities, and goals. They are primarily defined via `AGENT.md` and `agent.yaml`.

- **Engineering & Development:** `backend-engineer`, `frontend-engineer`, `database-engineer`, `devops-engineer`, `performance-engineer`, `security-engineer`, `architecture`, `coding`, `testing`, `qa`.
- **Product & Business:** `ceo`, `cto`, `product-founder`, `startup-founder-agent`, `product-manager`, `business-modeler`, `business-strategist`, `venture-capital-agent`, `investor-agent`.
- **Research & Analysis:** `research-director`, `customer-researcher`, `market-research`, `ux-researcher`, `competition-analyst-agent`, `trend-analyst-agent`, `scientific-analyst-agent`.
- **Marketing & Growth:** `marketing`, `growth-strategist`, `sales`, `seo`, `content-agent`.
- **System & Orchestration:** `orchestrator`, `evaluator`.

### Skill Categories (Overview)
Skills define discrete actionable capabilities, constraints, schemas, and logic. They are mapped via `SKILL.md` and `skill.yaml`.

- **Software Engineering:** `software-engineering`, `backend-engineering`, `frontend-engineering`, `database-design`, `cloud-deployment`, `testing-engineering`, `code-review`.
- **Business & Startups:** `business`, `startup-finance`, `startup-validation`, `pricing-strategy`, `market-intelligence`, `product-management`.
- **Data & Analytics:** `data-analysis`, `analytics`, `simulation`.
- **Science & Deep Tech:** `physics`, `advanced-physics`, `biology`, `chemistry`, `astronomy`, `scientific-research`.
- **Generative AI:** `prompt-engineering`, `image-generation`, `agent-design`.

## Integration Capabilities

The AI-Agent-OS **Kernel** dynamically bridges these ecosystems through its `AgentRegistry` and `SkillRegistry`. 

### Import Pipeline
1. **Auto-Discovery:** At boot, `PluginLoader` / `Genesis_Harness` integration scripts scan the configured directories.
2. **Metadata Extraction:** `agent.yaml` and `skill.yaml` are parsed. `AGENT.md` / `SKILL.md` form the system prompts.
3. **Dynamic Binding:** The `ModelRouter` maps necessary token budgets and provider capabilities to the incoming agents, whilst the `SkillRegistry` exposes available tools (Python functions, API calls, Docker executions) to the agent context.
4. **Execution Engine Allocation:** When a task is queued, the `AgentExecutionEngine` spawns an isolated execution context for the specific agent, binding the necessary skills in real-time.

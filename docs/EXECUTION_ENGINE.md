# EXECUTION ENGINE
## Overview
The Execution Engine provides a strict security boundary for agent task processing.

## Components
- **AgentRuntimeEngine**: Injects context, validates allowed tools, and invokes the Model Router.
- **SkillExecutionLayer**: Enforces strict RBAC to prevent unauthorized registry access or code execution.
- **WorkerSystem**: Enables high-throughput parallel execution of swarm tasks.

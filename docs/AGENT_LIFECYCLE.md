# AGENT LIFECYCLE
## Instantiation
Agents are dynamically loaded from `agents/registry.yaml`.

## Execution
1. Context injected from `MemoryManager`.
2. Tasks analyzed by `TaskRouter`.
3. Routing dynamically selected by `ModelRouter` (Claude/Gemini/DeepSeek).
4. Subtasks dispatched to isolated workers via `WorkerSystem`.
5. Outputs validated by `SupervisorEvaluator`.

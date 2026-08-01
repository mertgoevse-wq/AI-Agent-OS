# ORCHESTRATION
## Swarm Delegation
Tasks are parsed and classified by the `TaskRouter`, mapping them to explicit structural swarms (Engineering, AI, Architecture).

## Parallelization
The `WorkerSystem` wraps agent tasks in asynchronous `asyncio.gather` blocks, enforcing isolated execution limits.

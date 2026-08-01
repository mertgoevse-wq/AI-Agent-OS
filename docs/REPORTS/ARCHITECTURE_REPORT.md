# Architecture Report
## Overview
The AI-Agent-OS is currently at Phase 5. The core kernel supports async task execution, model routing, and an event bus.
## OMNI Upgrade Path
- **Lifecycle:** Move to a supervisor-driven swarm model where agents spawn sub-agents automatically.
- **Communication:** Enhance EventBus to support swarm broadcasting and directed inter-agent messaging.
- **Scalability:** The `InMemoryTaskQueue` must be abstracted to support distributed broker backends like Redis.

# Memory Architecture Report
## Overview
The system possesses STM, LTM (K/V), and a basic Vector Store (Knowledge).
## OMNI Upgrade Path
- **Episodic Memory:** Introduce episodic memory logging for agents to recall exact chronological sequences of past actions.
- **Persistent Vector DB:** The `InMemoryVectorStore` must be replaced with a persistent disk-backed database (e.g., ChromaDB) for true knowledge retention across reboots.

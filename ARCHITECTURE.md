# OMNI-Agent-OS Architecture

The system operates on an Autonomous Development Loop.

## Core Modules
- **`src/autonomous/loop.py`**: The main execution ring for agents.
- **`src/autonomous/qa_repair.py`**: Intervenes when tests fail and automatically assigns the Software Architect to repair bugs.
- **`src/models/provider_factory.py`**: Capable of dynamically routing to Anthropic, OpenAI, DeepSeek, Mistral, OpenRouter, and Ollama.
- **`src/mcp/integration_manager.py`**: Securely connects to external environments (Docker, FileSystem) to run code sandboxed.
- **`src/core/security.py`**: Vaults API keys using Fernet symmetric encryption at runtime.

## Application Layer (CryptoPilot-AI)
- **`src/cryptopilot/trading/strategy_engine.py`**: Executes complex trading signals.
- **`src/cryptopilot/trading/backtesting.py`**: Allows simulating strategies before deploying capital.

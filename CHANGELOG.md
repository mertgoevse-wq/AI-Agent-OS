# Changelog

## [3.0.0] - 2026-08-01 - "Autonomous Software Factory & CryptoPilot Productionization Phase"
### Added
- **Autonomous Engineering Pipeline (`src/autonomous/pipeline.py`)**:
  - Multi-agent software factory executing Planner -> Architect -> Developer -> QA -> Security -> Documentation.
  - Role agents: `PlannerAgent`, `ArchitectAgent`, `DeveloperAgent`, `QAAgent`, `SecurityAgent`, `DocumentationAgent`.
  - Integrated `QARepairEngine` self-repair loop.
- **CryptoPilot-AI Product Suite (`src/cryptopilot/`)**:
  - `PortfolioIntelligenceEngine`: Asset valuation and PnL breakdown.
  - `RiskEngine`: VaR (Value at Risk) and drawdown monitoring.
  - `MarketAnalyticsEngine`: Sentiment scoring and volatility index.
  - `AuthManager`: User authentication and session tokens.
  - `WorkspaceManager`: User workspace configurations.
  - `CryptoCopilotAssistant`: Interactive AI trading copilot.
- **UI Dashboard Enhancements**:
  - Real-time Risk Engine visualizer and Market Sentiment indicators in the Next.js frontend.
- **Unit Testing Suite**:
  - Expanded test coverage to **171 tests (100% pass rate)**.

## [2.0.0] - 2026-08-01 - "Autonomous Product Director Phase"
### Added
- Autonomous Development Loop (`src/autonomous/loop.py`).
- Self-Repair QA Engine (`src/autonomous/qa_repair.py`).
- `model_registry.yaml` supporting Anthropic, OpenAI, DeepSeek, Mistral, Gemini, OpenRouter, and Ollama.
- Prompt Engineering Templates (`omni_library/prompts/`).
- MCP Integration Manager with Secure Vaulting (`src/core/security.py`).

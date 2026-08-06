# CryptoPilot-AI (Powered by OMNI-Agent-OS)

![CryptoPilot-AI Dashboard](ui/public/logo.svg)

> **Commercial-Grade Autonomous AI Cryptocurrency Trading & Engineering Platform**

CryptoPilot-AI is an enterprise-grade AI financial intelligence platform powered by the **OMNI-Agent-OS** multi-agent kernel. It combines real-time portfolio tracking, quantitative AI trading strategies, autonomous risk management, and interactive AI market copilots with a self-improving multi-agent software factory.

---

## ⚡ Key Features

* **Autonomous Multi-Agent Software Factory**: Self-improving engineering loop (`Planner`, `Architect`, `Developer`, `QA`, `Security`, `Doc`) with automatic regression repair.
* **Multi-Provider LLM Router**: Seamless model switching across Anthropic, OpenAI, DeepSeek, Mistral, Gemini, OpenRouter, and local Ollama models.
* **Quantitative Strategy & Backtesting Engine**: Test trading strategies on historical data before live capital allocation.
* **AI Risk Management Engine**: Real-time Value at Risk (VaR 95%) calculation, max drawdown protection, position caps, and automated liquidations.
* **Interactive AI Copilot**: Real-time market copilot for trading advice, sentiment scoring, and automated execution.
* **Modern Next.js Dashboard**: Dark glassmorphism UI visualizer with live agent reasoning terminal, portfolio allocation graphs, and system telemetry.

---

## 🛠️ Quick Start

```bash
# 1. Start the OMNI-Agent-OS Backend API Server
python demo.py

# 2. Launch the Next.js Frontend Dashboard (in ui/ folder)
cd ui
npm run dev
```

Visit `http://localhost:3000` to interact with CryptoPilot-AI.

---

## 🧪 Testing & Verification

Run the comprehensive pytest suite:
```bash
python -m pytest tests/
```
**171 / 171 tests passing (100% pass rate).**

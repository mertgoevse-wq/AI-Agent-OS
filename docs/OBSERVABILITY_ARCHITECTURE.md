# AI-Agent-OS: Observability Architecture

Production-grade agent frameworks require intense observability because agents often execute non-deterministic workflows recursively.

## The Triad of Agent Observability

### 1. Traces (Distributed Agent Spans)
- Implemented via `TelemetryTracer` in `src/telemetry/observability.py`.
- Subscribes to the `EventBus` for `TASK_CREATED`, `TASK_COMPLETED`, and `TASK_FAILED`.
- Correlates Spans across `Supervisor` -> `Sub-Agent` invocations.

### 2. Metrics (Model Usage & Cost)
- Models charge per token. Unbounded autonomous loops can incur massive costs.
- The `ModelRouter` wraps every provider call and computes a `ModelUsageMetrics` struct (Prompt Tokens, Completion Tokens, Latency, Cost USD).
- These are attached to the Spans and published via the `EventBus`.

### 3. Structured Logging (History & Replays)
- `TaskHistory` is preserved in the `EventBus` memory and SQLite database.
- A future `ReplayEngine` will allow stepping backwards through a task's decision tree by reloading specific Agent Contexts at given log points.

## Downstream Integrations (Phase 5)
In downstream OS products (CryptoPilot-AI), these OpenTelemetry-compatible traces will be exported to Grafana/Datadog using standard OTLP exporters.

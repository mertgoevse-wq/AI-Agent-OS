# OMNI-Agent-OS Contribution Guidelines

Thank you for contributing to OMNI-Agent-OS!

## Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install UI dependencies: `cd ui && npm install`
4. Set up configurations in `configs/`

## Code Structure
- `src/` contains the Python core (MetaRouter, Autonomous Loop, Models).
- `configs/` contains YAML definitions for agents and skills.
- `ui/` contains the Next.js dashboard.
- `omni_library/` contains dynamic resources and prompts.

## Pull Request Process
1. Ensure all tests pass (`python -m pytest tests/`).
2. Do not introduce hardcoded values (e.g., API keys, static LLM logic).
3. Update relevant documentation in `docs/` and architecture Mermaid diagrams.

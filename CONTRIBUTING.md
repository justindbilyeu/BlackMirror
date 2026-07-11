# Contributing to BlackMirror

Thank you for considering contributing! This project is intentionally opinionated. Before opening a PR, please read the philosophy below.

## What We Accept

- New edge types – e.g., `amplifies`, `weakens`, `triggers`.
- New visualisers – TUI, web dashboard, Neo4j exporter.
- Integrations – LLM APIs for auto‑nutrient generation.
- Performance improvements – for graphs with >10k nodes.
- Better error messages – the CLI should be a gentle teacher.

## What We Do Not Accept

- Removing the falsifiability constraint.
- Allowing deletion or editing of scars (immutability is core).
- Adding external dependencies unless absolutely necessary.
- "Smoothing" the protocol – we keep the anti‑smoothing checks.

## Development Setup

```bash
git clone <your-fork>
cd blackmirror
pip install -e .
pytest tests/
```

## Code Style

- Follow PEP 8.
- Use type hints for all functions.
- Keep docstrings for every public API.
- Write tests for any new logic.

## Pull Request Process

1. Open an issue first to discuss non‑trivial changes.
2. Ensure tests pass locally.
3. Update the README if you change the CLI interface.
4. Link your PR to the relevant issue.

Thank you for helping us all think more clearly.

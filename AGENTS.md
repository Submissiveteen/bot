# AGENTS.md — Guidance for Codex

## Branch & Safety
- Work only on branch: updates_implementation_version_1.0.
- Never commit secrets. Ignore `.env`, use `.env.example` if needed.
- Prefer many small PR-ready commits (Conventional Commits).

## Commands (detect automatically; choose what applies)
- Python: `python -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -r requirements.txt || echo no-reqs`
- Node: `npm ci || npm install`
- Tests: `pytest -q || echo no-tests`; `npm test || echo no-tests`
- Lint/format: `ruff . || echo no-ruff`; `black --check . || echo no-black`; `eslint . || echo no-eslint`

## Artifacts to produce early
- repo_report.md, repo_metrics.json
- dr_index.md, dr_decisions.yaml
- plan/roadmap_v1.md, plan/tasks.json

## Review Gate
- After P0 (setup, lint, smoke tests): open PR to main with checklist.

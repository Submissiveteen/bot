# Plan README

This directory provides two roadmap options:

- `roadmap_v1.md`: conservative sequential plan. Used for `tasks.json`.
- `roadmap_v2.md`: aggressive batching allowing parallel work.

`tasks.json` follows V1 to minimize risks and ensure clear audit trail.

## Running tasks manually

From repository root:

```
ruff check .
ruff format .
black --check .
pytest -q
```

Run these commands after each change to verify linting, formatting, and tests.

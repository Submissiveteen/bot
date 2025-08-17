# Plan README

This directory provides two roadmap options, with V1 confirmed as the primary path:

- `roadmap_v1.md`: conservative sequential plan and source of truth for `tasks.json`.
- `roadmap_v2.md`: aggressive batching allowing parallel work (kept for reference only).

`tasks.json` follows V1 to minimize risks and ensure clear audit trail.

V1 will guide implementation going forward; V2 remains for historical context.

## Running tasks manually

From repository root:

```
ruff check .
ruff format .
black --check .
pytest -q
```

Run these commands after each change to verify linting, formatting, and tests.

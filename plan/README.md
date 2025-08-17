# Implementation Roadmap Plans

This directory contains two roadmap variants generated from documented requirements in `dr/analyses`:

- `roadmap_v1.md` – conservative sequencing in three phases (P0→P1→P2).
- `roadmap_v2.md` – aggressive plan with parallel batches inside each phase.
- `tasks.json` – machine-readable tasks derived from the aggressive plan (V2).

## Choosing V1 vs V2
- **V1** minimises risk by progressing sequentially. Use when capacity is limited or when strict gating is required before moving forward.
- **V2** groups work into parallel batches to shorten calendar time. Chosen for `tasks.json` because tasks are independent and share identical verification gates.

## Running Tasks Manually
For any task:
1. Ensure dependencies are installed: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
2. Execute verification gates:
   - `ruff check .`
   - `ruff format .`
   - `black --check .`
   - `pytest -q`
3. Provide proof of work with command output and list of changed files.

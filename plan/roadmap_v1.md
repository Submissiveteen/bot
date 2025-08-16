# Roadmap v1

## P0
- **DR_P0_001 – Fix dependencies and add dev tools**
  - changes: `requirements.txt`, `pyproject.toml`
  - commands: `pip install -r requirements.txt`, `ruff check .`, `ruff format .`, `black --check .`
  - DoD: dependencies install; lint/format pass
  - risk: low
- **DR_P0_002 – Enable pytest discovery**
  - changes: `pyproject.toml`, `crypto_decline_index/tests/__init__.py`
  - commands: `pytest -q`
  - DoD: tests run without ModuleNotFoundError
  - risk: low

## P1
_No DR analyses found._

## P2
_No DR analyses found._

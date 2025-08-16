# Repository Report

## Overview
Crypto On-Ramp Telegram Bot MVP that selects the best of five fiat-to-crypto aggregators and generates purchase deeplinks for users in Telegram【F:README.MD†L1-L13】

## File Tree and Roles
- `.env.example` – sample environment variables for local setup【F:.env.example†L3-L6】
- `AGENTS.md` – contributor guidance and task instructions.
- `README.MD`, `ROADMAP.MD`, `pre-summary.md`, `readmeMVP.md`, `research_pre_summary.md` – project documentation and research notes.
- `requirements.txt` – Python dependencies (contains duplicates and an invalid `python-dotenv>=` line causing installation failures)【F:requirements.txt†L1-L40】
- `main.py` – entry point launching the Telegram bot and registering router from `bot.buyer_handlers`【F:main.py†L1-L19】
- `bot/`
  - `__init__.py` – package marker.
  - `buyer_handlers.py` – script containing router setup and aggregator selection logic (stored as a code string; likely placeholder)【F:bot/buyer_handlers.py†L1-L86】
  - `handlers.py` – conversation flow handlers for the Telegram bot using FSM states and keyboards【F:bot/handlers.py†L1-L75】
  - `keyboards.py` – `ReplyKeyboardMarkup` definitions for user interactions【F:bot/keyboards.py†L1-L84】
  - `states.py` – finite-state machine states for bot dialogue【F:bot/states.py†L1-L23】
- `core/`
  - `aggregator_selector.py` – `AggregatorSelector` class choosing top aggregators based on country, method, amount, and KYC rules【F:core/aggregator_selector.py†L35-L75】
  - `deeplink_generator.py` – `DeeplinkGenerator` builds URLs by mapping parameters and ensuring required fields【F:core/deeplink_generator.py†L1-L26】
  - `utils.py` – validation helpers for wallet addresses and emails【F:core/utils.py†L1-L13】
- `crypto_decline_index/`
  - `scrape_decline_index.py` – standalone scraper calculating decline ratios from Trustpilot and Reddit reviews【F:crypto_decline_index/scrape_decline_index.py†L1-L75】
  - `decline_index.csv`, `table_on_ramp.csv` – input/output CSV data.
  - `requirements.txt` – dependencies for the scraper subproject.
  - `tests/test_decline.py` – pytest covering helper functions (fails because module import path `scrape_decline_index` is unresolved)【F:crypto_decline_index/tests/test_decline.py†L1-L40】
- `data/` – CSV/JSON datasets for aggregators and research PDFs used by core logic.
- `templates/messages_ru.json` – localization template (currently empty).
- `static/` – demo and roadmap images.
- `updates/21-9-43-Bot_Development_Roadmap_Analysis.json` – roadmap analysis artifact.

## Entry Points
1. `main.py` – runs the Telegram bot dispatcher.
2. `crypto_decline_index/scrape_decline_index.py` – executable script for decline index scraping.

## Dependencies & Configuration
- Primary packages: `aiogram`, `pandas`, `requests`, `cloudscraper`, `beautifulsoup4`, `pytest`, etc., pinned in `requirements.txt`【F:requirements.txt†L1-L37】
- Duplicate entries (`pydantic`, `pandas`) and unfinished spec `python-dotenv>=` introduce installation risk.
- Environment configuration sourced from `.env` (sample in `.env.example`).
- Additional subproject requirements in `crypto_decline_index/requirements.txt`.

## Import/Dependency Graph
```
main.py
└── bot.buyer_handlers
    ├── core.aggregator_selector
    ├── core.deeplink_generator
    └── aiogram (router, states, keyboards)
bot.handlers → bot.states, bot.keyboards
crypto_decline_index.scrape_decline_index → requests, BeautifulSoup, pandas
```

## Tests & CI
- Pytest suite located at `crypto_decline_index/tests`; running `pytest -q` fails due to missing module path (`scrape_decline_index`)【73ecec†L1-L19】
- No continuous integration config found.
- Smoke tests could be added for bot startup and aggregator selection using small sample datasets.

## Technical Debt
- Invalid and duplicate entries in `requirements.txt` cause dependency installation errors【0871cb†L1-L4】
- `bot/buyer_handlers.py` embeds code as a string and writes files, complicating imports.
- `scrape_decline_index.py` executes on import and lacks a `main()` function referenced by tests.
- Empty `templates/messages_ru.json` and tracked artifacts (`.DS_Store`, compiled `__pycache__` file) indicate repository hygiene issues.
- Tests and linters currently fail; CI absent.

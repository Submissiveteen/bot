"""aggregator_engine.py – advanced engine with tier, cluster, method‑aware scoring.

Assumptions
-----------
* CSVs (table_1.csv, table_2.csv, table_4.csv) live in `data/`.
* Country → cluster mapping stored in `data/cluster_map.yaml` (fallback = hard‑coded).
* YAML `weights.yml` may override DEFAULT_WEIGHTS (hot‑reloaded every 5 min).
* Decline & fee columns are now suffixed by payment method (e.g. `Fee_Card`,
  `Decline_SEPA`). Plain `TypicalFeePct` / `CardDeclineRate` act as fallback.
* KYC_Complexity column (0–4) exists; if missing → derived from `KYC_Docs`.
* Assets supported stored in `SupportedAssets` (comma‑sep) in table_1.

The goal is correctness > micro‑performance; heavy data is cached & thread‑safe.
"""
import logging
import os
import threading
from pathlib import Path
import pandas as pd
import yaml
from typing import Dict, Optional, Tuple

# Configurable data directory
_DATA_DIR = Path(os.getenv("AGG_ENGINE_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))

_DEFAULT_CLUSTER_MAP = {
    "DE": "EU_SEPA", "FR": "EU_SEPA", "FI": "NORDICS",
    "SE": "NORDICS", "EE": "BALTICS", "LT": "BALTICS", "LV": "BALTICS",
    "CA": "CA", "CH": "EFTA_CH", "GB": "UK"
}

_DEFAULT_TIERS = {
    "TIER1": 500,
    "TIER2": 2000,
    "TIER3": float("inf")
}

class _CachedValue:
    def __init__(self, loader, ttl: int):
        self.loader = loader
        self.ttl = ttl
        self.lock = threading.RLock()
        self._value = None
        self._expires_at = 0

    def get(self):
        with self.lock:
            now = time.time()
            if self._value is None or now >= self._expires_at:
                self._value = self.loader()
                self._expires_at = now + self.ttl
            return self._value

class AggregatorEngine:
    def __init__(self):
        self._data = _CachedValue(self._load_data, ttl=600)
        self._weights = _CachedValue(self._load_weights, ttl=300)
        self._cluster_map = self._load_cluster_map()
        self._tiers = self._load_tier_thresholds()
        self._mutex = threading.RLock()

    def _load_cluster_map(self) -> Dict[str, str]:
        p = _DATA_DIR / "cluster_map.yaml"
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logging.exception("Failed to load cluster_map.yaml")
        logging.warning("cluster_map.yaml not found; using fallback clusters")
        return _DEFAULT_CLUSTER_MAP

    def _load_tier_thresholds(self) -> Dict[str, float]:
        path = _DATA_DIR / "tier_thresholds.yml"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logging.exception("Failed to load tier_thresholds.yml")
        return _DEFAULT_TIERS

    def generate_deeplink(self, aggregator: str, amount: float, fiat: str, crypto: str,
                           wallet: str, partner_secret: str | None = None,
                           extra_params: Optional[Dict[str, str]] = None) -> str:
        df_meta, _ = self._data.get()
        rows = df_meta[df_meta["Aggregator"] == aggregator]
        if rows.empty:
            raise ValueError(f"Aggregator '{aggregator}' not found in metadata")
        row = rows.iloc[0]

        template = row.get("DeeplinkTemplate", "")
        params = {"amount": str(amount), "fiat": fiat, "crypto": crypto, "wallet": wallet}
        if extra_params:
            params.update(extra_params)

        if "${signature}" in template:
            if aggregator.lower() in _SIGNATURE_REGISTRY:
                if not partner_secret:
                    raise ValueError("partner_secret required for signature")
                strategy = _SIGNATURE_REGISTRY[aggregator.lower()]
                params["signature"] = strategy.sign(params, partner_secret)
            else:
                logging.warning(f"Aggregator '{aggregator}' has signature placeholder but no strategy defined")

        for k, v in params.items():
            template = template.replace(f"${{{k}}}", v)
        return template

    def _infer_kyc(self, docs: str | None) -> int:
        if not docs:
            return 0
        docs_l = docs.lower()
        patterns = {
            2: ["passport", "government", "gov", "id"],
            3: ["poa"],
            4: ["source of funds", "income", "bank statement"]
        }
        for level, keys in patterns.items():
            for key in keys:
                if re.search(rf"\\b{key}\\b", docs_l):
                    return level
        return 1

    def _country_to_cluster(self, iso: str) -> str:
        return self._cluster_map.get(iso.upper(), "EU_SEPA")


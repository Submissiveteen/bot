import logging
import os
import re
import threading
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import yaml

from core.utils import load_yaml_config, CachedValue
from core.logging_config import setup_logging
from core.signature import SIGNATURE_REGISTRY
from core.deeplink_builder import DeeplinkBuilder, validate_deeplink_params, inject_signature

setup_logging()

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
builder = DeeplinkBuilder(template)
params = inject_signature(name, params, secret)
deeplink = builder.render(params)

class AggregatorEngine:
    def __init__(self):
        self._data = CachedValue(self._load_data, ttl=600)
        self._weights = CachedValue(self._load_weights, ttl=300)
        self._cluster_map = load_yaml_config(_DATA_DIR / "cluster_map.yaml", fallback=_DEFAULT_CLUSTER_MAP)
        self._tiers = load_yaml_config(Path("config/tier_thresholds.yml"), fallback=_DEFAULT_TIERS)
        self._mutex = threading.RLock()

    def generate_deeplink(self, aggregator: str, amount: float, fiat: str, crypto: str,
                           wallet: str, partner_secret: Optional[str] = None,
                           extra_params: Optional[Dict[str, str]] = None) -> str:
        row = self._get_aggregator_row(aggregator)
        template = row.get("DeeplinkTemplate", "")
        params = self._build_deeplink_params(amount, fiat, crypto, wallet, extra_params)

        if "${signature}" in template:
            params = self._inject_signature(aggregator, params, partner_secret, template)

        return self._substitute_template(template, params)

    def _get_aggregator_row(self, aggregator: str):
        df_meta, _ = self._data.get()
        rows = df_meta[df_meta["Aggregator"] == aggregator]
        if rows.empty:
            raise ValueError(f"Aggregator '{aggregator}' not found in metadata")
        return rows.iloc[0]

    def _build_deeplink_params(self, amount, fiat, crypto, wallet, extra):
        params = {"amount": str(amount), "fiat": fiat, "crypto": crypto, "wallet": wallet}
        if extra:
            params.update(extra)
        return params

    def _inject_signature(self, aggregator, params, secret, template):
        if aggregator.lower() in SIGNATURE_REGISTRY:
            if not secret:
                raise ValueError("partner_secret required for signature")
            strategy = SIGNATURE_REGISTRY[aggregator.lower()]
            params["signature"] = strategy.sign(params, secret)
        else:
            logging.warning(f"Aggregator '{aggregator}' has signature placeholder but no strategy defined")
        return params

    def _substitute_template(self, template, params):
        for k, v in params.items():
            template = template.replace(f"${{{k}}}", v)
        return template

    def _infer_kyc(self, docs: Optional[str]) -> int:
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
                if re.search(rf"\b{key}\b", docs_l):
                    return level
        return 1

    def _country_to_cluster(self, iso: str) -> str:
        return self._cluster_map.get(iso.upper(), "EU_SEPA")

    def _load_data(self):
        # Should implement loading of metadata and ratings DataFrames
        raise NotImplementedError

    def _load_weights(self):
        # Should implement weight configuration loading
        raise NotImplementedError

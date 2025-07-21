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
from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd
import yaml

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ---------------------------------------------------------------------------
# Utilities & models
# ---------------------------------------------------------------------------
PAYMENT_METHODS = {
    "CARD": {"aliases": {"visa", "mastercard", "card", "credit card"}},
    "SEPA": {"aliases": {"sepa", "bank transfer", "bank"}},
    "ACH": {"aliases": {"ach", "wire"}},
    "APPLE_PAY": {"aliases": {"apple pay"}},
    "GOOGLE_PAY": {"aliases": {"google pay"}},
    "MOBILE": {"aliases": {"mobile", "revolut", "monobank"}},
}

DEFAULT_WEIGHTS = {
    "fee": 0.35,
    "decline": 0.25,
    "kyc": 0.2,
    "tier_match": 0.1,
    "cluster": 0.1,
}

_WEIGHTS_PATH = _DATA_DIR / "weights.yml"
_WEIGHTS_TTL = 300  # seconds

# Tier constants
Tier = Literal["TIER1", "TIER2", "TIER3"]

# KYC complexity scale
KYC_SCALE = {
    "none": 0,
    "email": 0,
    "basic": 1,  # name, dob
    "id": 2,  # passport / id + selfie
    "poa": 3,
    "sof": 4,  # source of funds
}

@dataclass
class ScoreBreakdown:
    fee: float
    decline: float
    kyc: float
    tier_match: float
    cluster: float
    total: float

# ---------------------------------------------------------------------------
class SignatureStrategy:
    """Base class for per‑provider signature calculation."""

    def sign(self, params: Dict[str, str], secret: str) -> str:
        raise NotImplementedError


class HMACSHA256Signature(SignatureStrategy):
    def __init__(self, ordered_keys: Optional[List[str]] = None):
        self._ordered_keys = ordered_keys

    def sign(self, params: Dict[str, str], secret: str) -> str:
        if self._ordered_keys:
            msg = "".join(params[k] for k in self._ordered_keys if k in params)
        else:
            # sort keys for deterministic order
            msg = "".join(params[k] for k in sorted(params))
        return hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()


_SIGNATURE_REGISTRY: Dict[str, SignatureStrategy] = {
    "banxa": HMACSHA256Signature(),
    "paybis": HMACSHA256Signature(["partnerId", "cryptoAddress", "currencyCodeFrom", "currencyCodeTo", "fiatAmount"]),
    "transak": HMACSHA256Signature(),  # real Transak uses SHA512; placeholder
}

# ---------------------------------------------------------------------------
class _CachedValue:
    """Thread‑safe TTL cache cell"""

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
    """Tier / cluster / method aware aggregator selector."""

    def __init__(self):
        self._data = _CachedValue(self._load_data, ttl=600)
        self._weights = _CachedValue(self._load_weights, ttl=_WEIGHTS_TTL)
        self._cluster_map = self._load_cluster_map()
        self._mutex = threading.RLock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def shortlist(
        self,
        country_iso: str,
        amount_eur: float,
        payment_method: str,
        crypto: str,
        avoid_kyc: bool = False,
        desired_kyc_level: int = 1,  # 0‑basic, 1‑ID‑okay, etc.
        top_n: int = 3,
    ) -> List[Tuple[str, ScoreBreakdown]]:
        payment_method_key = self._normalize_method(payment_method)
        cluster = self._country_to_cluster(country_iso)
        tier = self._calc_tier(amount_eur)

        df_meta, df_rating = self._data.get()
        weights = self._weights.get()

        # ---------- Prefilter ----------
        candidates = df_meta.copy()

        # asset support
        asset_mask = candidates["SupportedAssets"].str.contains(crypto, na=False, case=False)
        candidates = candidates[asset_mask]

        # cluster support
        cluster_mask = candidates[f"{cluster}_Supported"] == True  # noqa: E712
        candidates = candidates[cluster_mask]

        # payment method support
        pm_mask = candidates["PaymentMethods"].str.contains(payment_method_key, case=False, na=False)
        candidates = candidates[pm_mask]

        # tier limit check
        within_limit = candidates["MaxEur"].fillna(float("inf")) >= amount_eur
        candidates = candidates[within_limit]

        if candidates.empty:
            return []

        # merge with rating 🟢 / 🟠 / 🟥 flags
        tier_col = f"{payment_method_key.capitalize()}_{tier}"
        flags = df_rating[["Cluster", tier_col]].rename(columns={tier_col: "FlagProvider"})
        candidates = candidates.merge(flags, how="left", left_on="Aggregator", right_on="FlagProvider")
        # mark red flag
        candidates["is_red"] = candidates[tier_col].str.contains("🟥", na=False)
        # penalize red

        scored: List[Tuple[str, ScoreBreakdown]] = []
        for _, row in candidates.iterrows():
            score_bd = self._score_row(row, payment_method_key, tier, cluster, avoid_kyc, desired_kyc_level, weights)
            if score_bd.total > 0:
                scored.append((row["Aggregator"], score_bd))

        scored.sort(key=lambda x: x[1].total, reverse=True)
        return scored[:top_n]

    def generate_deeplink(
        self,
        aggregator: str,
        amount: float,
        fiat: str,
        crypto: str,
        wallet: str,
        partner_secret: str | None = None,
        extra_params: Optional[Dict[str, str]] = None,
    ) -> str:
        df_meta, _ = self._data.get()
        row = df_meta[df_meta["Aggregator"] == aggregator].iloc[0]
        template = row["DeeplinkTemplate"]
        params = {
            "amount": str(amount),
            "fiat": fiat,
            "crypto": crypto,
            "wallet": wallet,
        }
        if extra_params:
            params.update(extra_params)

        # signature if needed
        if "${signature}" in template:
            strategy = _SIGNATURE_REGISTRY.get(aggregator.lower(), HMACSHA256Signature())
            if not partner_secret:
                raise ValueError("partner_secret required for signature")
            params["signature"] = strategy.sign(params, partner_secret)

        # simple placeholder replacement
        for k, v in params.items():
            template = template.replace(f"${{{k}}}", v)
        return template

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _load_weights() -> Dict[str, float]:
        if _WEIGHTS_PATH.exists():
            try:
                with open(_WEIGHTS_PATH, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                return {**DEFAULT_WEIGHTS, **data}
            except Exception:
                return DEFAULT_WEIGHTS
        return DEFAULT_WEIGHTS

    @staticmethod
    def _normalize_method(method: str) -> str:
        m = method.lower()
        for key, cfg in PAYMENT_METHODS.items():
            if m == key.lower() or m in cfg["aliases"]:
                return key
        return method.upper()

    @staticmethod
    def _calc_tier(amount: float, nonkyc: float | None = None) -> Tier:
        if nonkyc is None or nonkyc == 0:
            # fallback: simple heuristic
            if amount <= 500:
                return "TIER1"
            if amount <= 2000:
                return "TIER2"
            return "TIER3"
        if amount <= nonkyc:
            return "TIER1"
        if amount <= 4 * nonkyc:
            return "TIER2"
        return "TIER3"

    def _score_row(
        self,
        row: pd.Series,
        pm: str,
        tier: Tier,
        cluster: str,
        avoid_kyc: bool,
        desired_kyc: int,
        w: Dict[str, float],
    ) -> ScoreBreakdown:
        # Fee score (lower is better)
        fee_col = f"Fee_{pm.capitalize()}"
        fee_pct = row.get(fee_col) or row.get("TypicalFeePct") or 5.0
        fee_score = max(0.0, 1 - fee_pct / 10)  # assume 10 % = worst 0

        # Decline score (lower is better)
        decline_col = f"Decline_{pm.capitalize()}"
        decline_pct = row.get(decline_col) or row.get("CardDeclineRate") or 50.0
        decline_score = max(0.0, 1 - decline_pct / 100)

        # KYC score: prefer lower complexity
        prov_kyc = int(row.get("KYC_Complexity", self._infer_kyc(row.get("KYC_Docs", ""))))
        kyc_gap = max(0, prov_kyc - desired_kyc)
        kyc_score = 1 - (kyc_gap / 4)
        if avoid_kyc and prov_kyc > 0:
            kyc_score -= 0.2  # extra penalty

        # Tier match bonus (1 if provider rated 🟢, 0.5 🟠, 0 for 🟥/None)
        flag_field = row.get("FlagProvider")
        if isinstance(flag_field, str):
            if "🟢" in flag_field:
                tier_score = 1.0
            elif "🟠" in flag_field:
                tier_score = 0.5
            else:
                tier_score = 0.0
        else:
            tier_score = 0.0
        # Red flag explicit penalty
        if row.get("is_red", False):
            tier_score -= 0.5

        # Cluster score is binary (supported already filtered)
        cluster_score = 1.0

        total = (
            fee_score * w["fee"]
            + decline_score * w["decline"]
            + kyc_score * w["kyc"]
            + tier_score * w["tier_match"]
            + cluster_score * w["cluster"]
        )
        return ScoreBreakdown(fee_score, decline_score, kyc_score, tier_score, cluster_score, total)

    # ------------------------------------------------------------------
    def _load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        meta = pd.read_csv(_DATA_DIR / "table_1.csv")
        rating = pd.read_csv(_DATA_DIR / "table_2.csv")

        # basic cleaning
        meta.columns = [c.strip() for c in meta.columns]
        for col in [c for c in meta.columns if "Fee" in c or "Decline" in c or "Limit" in c or "Eur" in c or "Pct" in c]:
            meta[col] = (
                meta[col]
                .astype(str)
                .str.replace("%", "")
                .str.replace(",", ".")
                .str.replace(" ", "")
                .astype(float, errors="ignore")
            )
        # derive MaxEur column
        if "Min/Max" in meta.columns:
            meta["MaxEur"] = (
                meta["Min/Max"]
                .astype(str)
                .str.split("/", expand=True)[1]
                .str.replace(" ", "")
                .astype(float, errors="ignore")
            )
        return meta, rating

    # ------------------------------------------------------------------
    def _load_cluster_map(self) -> Dict[str, str]:
        p = _DATA_DIR / "cluster_map.yaml"
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        # fallback minimal
        return {
            "DE": "EU_SEPA",
            "FR": "EU_SEPA",
            "FI": "NORDICS",
            "SE": "NORDICS",
            "EE": "BALTICS",
            "LT": "BALTICS",
            "LV": "BALTICS",
            "CA": "CA",
            "CH": "EFTA_CH",
            "GB": "UK",
        }

    def _country_to_cluster(self, iso: str) -> str:
        return self._cluster_map.get(iso.upper(), "EU_SEPA")

    @staticmethod
    def _infer_kyc(docs: str | None) -> int:
        if not docs:
            return 0
        docs_l = docs.lower()
        if "passport" in docs_l or "gov" in docs_l:
            return 2
        if "poa" in docs_l:
            return 3
        if "source" in docs_l:
            return 4
        return 1

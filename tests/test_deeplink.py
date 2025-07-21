import pytest
from core.aggregator_engine import AggregatorEngine
import os

os.environ["AGG_ENGINE_DATA_DIR"] = "data"

def test_country_to_cluster():
    engine = AggregatorEngine()
    assert engine._country_to_cluster("DE") == "EU_SEPA"
    assert engine._country_to_cluster("ZZ") == "EU_SEPA"

def test_infer_kyc():
    engine = AggregatorEngine()
    assert engine._infer_kyc("passport") == 2
    assert engine._infer_kyc("source of funds") == 4
    assert engine._infer_kyc("") == 0

def test_generate_deeplink_happy():
    engine = AggregatorEngine()
    link = engine.generate_deeplink("bitvalex", 100, "EUR", "BTC", "wallet123", "mysecret")
    assert link.startswith("http")
    assert "wallet123" in link

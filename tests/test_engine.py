import pytest
from core.aggregator_engine import AggregatorEngine

def test_infer_kyc():
    engine = AggregatorEngine()
    assert engine._infer_kyc("passport") == 2
    assert engine._infer_kyc("source of funds") == 4
    assert engine._infer_kyc("some utility bill") == 1
    assert engine._infer_kyc("") == 0

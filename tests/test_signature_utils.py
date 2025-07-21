import pytest
from core.signature import get_signature_strategy
from core.utils import CachedValue
import time

def test_signature_registry():
    strat = get_signature_strategy("bitvalex")
    assert strat is not None
    sig = strat.sign({"a": "1", "b": "2"}, "secret")
    assert isinstance(sig, str)
    assert len(sig) == 64

def test_cached_value():
    state = {"calls": 0}

    def loader():
        state["calls"] += 1
        return "data"

    cached = CachedValue(loader, ttl=1)
    assert cached.get() == "data"
    assert cached.get() == "data"
    assert state["calls"] == 1
    time.sleep(1.1)
    assert cached.get() == "data"
    assert state["calls"] == 2

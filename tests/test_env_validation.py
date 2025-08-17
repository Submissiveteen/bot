import pytest
from core.utils import validate_environment


def test_validate_environment_success(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("BITVALEX_SECRET", "y")
    monkeypatch.setenv("CRYPTOMUS_SECRET", "z")
    validate_environment()


def test_validate_environment_missing(monkeypatch):
    for key in ["BOT_TOKEN", "BITVALEX_SECRET", "CRYPTOMUS_SECRET"]:
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError):
        validate_environment()

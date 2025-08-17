import integrations.status as status
from core.utils import dummy_service_ok, dummy_service_status, secure_service_ok


def test_dummy_service_ok(monkeypatch):
    monkeypatch.setattr(status, "ping", lambda url="", timeout=5: 200)
    assert dummy_service_ok()


def test_dummy_service_timeout(monkeypatch):
    monkeypatch.setattr(status, "ping", lambda url="", timeout=5: 0)
    assert dummy_service_status() == "timeout"
    assert not dummy_service_ok()


def test_secure_service_ok(monkeypatch):
    monkeypatch.setattr(status, "secure_ping", lambda url, timeout=5: 200)
    assert secure_service_ok("https://example.com")

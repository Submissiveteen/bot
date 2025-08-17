import requests
from integrations import status


def test_ping_returns_200(monkeypatch):
    class Resp:
        status_code = 200

    def fake_get(url, timeout=5):
        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    assert status.ping() == 200


def test_ping_timeout(monkeypatch):
    def fake_get(url, timeout=5):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(requests, "get", fake_get)
    assert status.ping(timeout=1) == 0


def test_secure_ping_requires_https():
    assert status.secure_ping("http://example.com") == 0

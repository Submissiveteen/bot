import integrations.status as status
from bot.handlers import (
    get_farewell_message,
    get_service_status_message,
    get_start_message,
    get_secure_service_message,
)


def test_get_start_message():
    assert get_start_message() == "Начать"


def test_service_status_timeout(monkeypatch):
    monkeypatch.setattr(status, "ping", lambda url="", timeout=5: 0)
    assert get_service_status_message() == "Сервис не отвечает"


def test_service_status_ok(monkeypatch):
    monkeypatch.setattr(status, "ping", lambda url="", timeout=5: 200)
    assert get_service_status_message() == "Сервис доступен"


def test_get_farewell_message():
    assert get_farewell_message() == "До свидания"


def test_get_secure_service_message_insecure():
    assert get_secure_service_message("http://bad.com") == "Небезопасный URL"

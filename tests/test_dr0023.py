from core import utils


def test_service_up_returns_true():
    assert utils.service_up("https://httpbin.org/status/200")

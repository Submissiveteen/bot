from core import utils


def test_delayed_ping_returns_200():
    assert utils.delayed_httpbin_ping(1) == 200

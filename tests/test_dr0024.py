from core import utils


def test_head_service_status_returns_200():
    assert utils.head_service_status("https://httpbin.org/status/200") == 200

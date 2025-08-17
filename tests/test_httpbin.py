from integrations.httpbin import ping


def test_ping_returns_200():
    assert ping() == 200

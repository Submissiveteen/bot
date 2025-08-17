import requests


def ping() -> int:
    """Return HTTP status from httpbin test endpoint."""
    resp = requests.get("https://httpbin.org/status/200", timeout=5)
    return resp.status_code

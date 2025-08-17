import requests


def ping() -> int:
    """Return HTTP status from httpbin test endpoint."""
    resp = requests.get("https://httpbin.org/status/200", timeout=5)
    return resp.status_code


def delayed_ping(delay: int = 1) -> int:
    """Return status code from delayed httpbin endpoint."""
    resp = requests.get(f"https://httpbin.org/delay/{delay}", timeout=delay + 5)
    return resp.status_code

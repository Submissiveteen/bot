"""Simple HTTP status utilities."""

import requests


def ping(url: str = "https://httpbin.org/status/200", timeout: int = 5) -> int:
    """Return HTTP status code for given URL or 0 on timeout."""
    try:
        resp = requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout:
        return 0
    return resp.status_code


def secure_ping(url: str, timeout: int = 5) -> int:
    """Ping only HTTPS endpoints; return 0 for insecure URLs."""
    if not url.startswith("https://"):
        return 0
    return ping(url, timeout=timeout)

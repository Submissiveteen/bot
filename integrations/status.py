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


def is_service_up(url: str, timeout: int = 5) -> bool:
    """Return True if service responds with HTTP 200."""
    return ping(url, timeout=timeout) == 200


def head_ping(url: str = "https://httpbin.org/status/200", timeout: int = 5) -> int:
    """Perform HEAD request and return status code."""
    try:
        resp = requests.head(url, timeout=timeout)
        return resp.status_code
    except requests.exceptions.Timeout:
        return 0

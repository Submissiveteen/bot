import os
import re
import time
import uuid
from pathlib import Path
from typing import Dict

import logging
import yaml

from integrations import httpbin, status as status_integration


def load_yaml_config(path: Path, fallback: dict | None = None) -> dict:
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return fallback or {}


def validate_environment() -> None:
    """Verify required environment variables are present and non-empty."""
    required_keys = ["BOT_TOKEN", "BITVALEX_SECRET", "CRYPTOMUS_SECRET"]
    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        logging.error(f"Missing required environment variables: {missing}")
        raise RuntimeError("Missing required env vars: " + ", ".join(missing))


def normalize_currency(value: str) -> str:
    value = value.strip().upper()
    aliases = {"EURO": "EUR", "USDOLLAR": "USD", "DOLLAR": "USD"}
    return aliases.get(value, value)


class CachedValue:
    def __init__(self, loader, ttl: int = 300):
        self._loader = loader
        self._ttl = ttl
        self._value = None
        self._expires = 0

    def get(self):
        if time.time() > self._expires:
            self._value = self._loader()
            self._expires = time.time() + self._ttl
        return self._value


def validate_wallet_address(address: str) -> bool:
    """Простейшая валидация крипто-адреса (расширяется под нужные сети)"""
    return bool(
        re.match(
            r"^(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|[a-zA-Z0-9]{26,35})$",
            address,
        )
    )


def validate_email(email: str) -> bool:
    """Простая валидация email"""
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))


def normalize_country(name: str) -> str:
    """Return lowercased country name without surrounding spaces."""
    return name.strip().lower()


# ---- DR_0003–DR_0008 helpers (из bundle) ----


def generate_uuid() -> str:
    """Return random UUID string."""
    return str(uuid.uuid4())


def get_client_ip(headers: Dict[str, str]) -> str:
    """Extract client IP from headers."""
    forwarded = headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return headers.get("X-Real-IP", "")


def default_headers() -> Dict[str, str]:
    """Return default headers with request ID."""
    return {"User-Agent": "bot", "X-Request-ID": generate_uuid()}


def dummy_service_status() -> str:
    """Return status of dummy integration: ok/fail/timeout."""
    code = status_integration.ping()
    if code == 200:
        return "ok"
    if code == 0:
        return "timeout"
    return "fail"


def dummy_service_ok() -> bool:
    """Check dummy integration health."""
    return dummy_service_status() == "ok"


def secure_service_ok(url: str) -> bool:
    """Return True if URL is HTTPS and responds with 200."""
    return status_integration.secure_ping(url) == 200


def delayed_httpbin_ping(delay: int = 1) -> int:
    """Proxy to httpbin delayed endpoint returning its status code."""
    return httpbin.delayed_ping(delay)


def service_up(url: str) -> bool:
    """Check if service responds with HTTP 200."""
    return status_integration.is_service_up(url)


def head_service_status(url: str) -> int:
    """Return status code from HEAD request to service."""
    return status_integration.head_ping(url)

import re

from integrations import status as status_integration


def validate_wallet_address(address: str) -> bool:
    """
    Простейшая валидация крипто-адреса (расширяется под нужные сети)
    """
    return bool(
        re.match(
            r"^(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|[a-zA-Z0-9]{26,35})$",
            address,
        )
    )


def validate_email(email: str) -> bool:
    """
    Простая валидация email
    """
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))


def normalize_country(name: str) -> str:
    """Return lowercased country name without surrounding spaces."""
    return name.strip().lower()


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

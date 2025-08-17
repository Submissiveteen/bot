import re


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

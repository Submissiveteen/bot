import re

# Predefined patterns for certain cryptocurrencies
_ADDRESS_PATTERNS = {
    "ETH": re.compile(r"^0x[0-9A-Fa-f]{40}$"),
    "BTC": re.compile(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$"),
}

_GENERIC_ADDRESS_PATTERN = re.compile(r"^[A-Za-z0-9]{20,}$")


def is_valid_amount(amount: float) -> bool:
    """Check if the amount is positive."""
    return amount > 0


def is_valid_wallet(address: str, crypto: str) -> bool:
    """Basic format validation for a cryptocurrency wallet address."""
    pattern = _ADDRESS_PATTERNS.get(crypto.upper())
    if pattern:
        return bool(pattern.match(address))
    return bool(_GENERIC_ADDRESS_PATTERN.match(address))

from core.utils import (
    normalize_country,
    validate_email,
    validate_wallet_address,
)


def test_normalize_country():
    assert normalize_country(" Ukraine ") == "ukraine"


def test_validate_email():
    assert validate_email("user@example.com")
    assert not validate_email("bad-email")


def test_validate_wallet_address():
    assert validate_wallet_address("0x" + "a" * 40)
    assert not validate_wallet_address("not_a_wallet")

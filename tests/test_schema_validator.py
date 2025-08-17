from core.schema_validator import is_valid_amount, is_valid_wallet


def test_is_valid_amount():
    assert is_valid_amount(1.0)
    assert not is_valid_amount(0)
    assert not is_valid_amount(-5)


def test_is_valid_wallet():
    assert is_valid_wallet("0x" + "a" * 40, "ETH")
    assert not is_valid_wallet("zzz", "ETH")

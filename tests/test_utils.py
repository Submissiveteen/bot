from core.utils import normalize_country


def test_normalize_country():
    assert normalize_country(" Ukraine ") == "ukraine"

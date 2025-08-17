import importlib
from pathlib import Path

import pytest

SRC = importlib.import_module("scrape_decline_index")


# ——— fixtures ———
@pytest.fixture()
def html_sample():
    return "<html><body><p>Card declined twice</p><p>Got coins ✅</p></body></html>"


@pytest.fixture()
def reddit_json():
    obj = {
        "data": {
            "children": [
                {"data": {"body": "payment failed"}},
                {"data": {"body": "all good"}},
            ]
        }
    }
    return obj


# ——— tests ———
def test_decline_ratio():
    texts = ["declined", "fail", "ok"]
    assert SRC.decline_ratio(texts) == 0.667


def test_tp_parser(html_sample):
    soup = SRC.BeautifulSoup(html_sample, "html.parser")
    texts = [p.get_text(strip=True).lower() for p in soup.select("p")]
    assert texts == ["card declined twice", "got coins ✅"]


def test_reddit_comments_json(monkeypatch, reddit_json):
    #   mock _get → вернёт reddit_json
    monkeypatch.setattr(SRC, "_get", lambda *a, **k: reddit_json)
    out = SRC.reddit_comments("Transak", 10)
    assert "payment failed" in out and "all good" in out


def test_full_flow(monkeypatch, html_sample, reddit_json, tmp_path: Path):
    #   patch HTTP calls to avoid network
    def fake_get(url, *a, **k):
        if "trustpilot" in url:
            return html_sample
        return reddit_json

    monkeypatch.setattr(SRC, "_get", fake_get)

    #   run main() inside temp dir
    with monkeypatch.context() as m:
        m.chdir(tmp_path)
        m.setattr(SRC, "CSV_OUTPUT", Path("decline_index.csv"))
        m.setattr(SRC, "AGGREGATORS", ["Transak"])
        assert SRC.main() == 0
        assert Path("decline_index.csv").exists()
        df = SRC.pd.read_csv("decline_index.csv")
        assert not df.empty

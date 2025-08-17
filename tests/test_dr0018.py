from pathlib import Path


def test_dr0018_note_present():
    content = Path("docs/compliance/README.md").read_text(encoding="utf-8")
    assert "DR_0018" in content

import json
from pathlib import Path


def test_compliance_note_present():
    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    assert "compliance_note" in data

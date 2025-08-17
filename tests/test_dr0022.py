import json
from pathlib import Path


def test_dr0022_message_present():
    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    assert "dr0022_notice" in data

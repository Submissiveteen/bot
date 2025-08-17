import json
from pathlib import Path


def test_dr0019_message_present():
    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    assert "dr0019_notice" in data

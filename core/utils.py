import yaml
import time
from pathlib import Path

def load_yaml_config(path: Path, fallback: dict = None) -> dict:
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return fallback or {}

class CachedValue:
    def __init__(self, loader, ttl=300):
        self._loader = loader
        self._ttl = ttl
        self._value = None
        self._expires = 0

    def get(self):
        if time.time() > self._expires:
            self._value = self._loader()
            self._expires = time.time() + self._ttl
        return self._value

import yaml
from jsonschema import validate, ValidationError
from pathlib import Path

AGGREGATOR_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "url_template": {"type": "string"},
            "supported_fiat": {"type": "array", "items": {"type": "string"}},
            "supported_crypto": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["name", "url_template", "supported_fiat", "supported_crypto"]
    }
}

def validate_yaml_file(path: Path, schema: dict):
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as ve:
        print(f"YAML Validation Error: {ve.message}")
        return False

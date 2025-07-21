import logging
import logging.config
import yaml
from pathlib import Path

def setup_logging(config_path: Path = Path("config/logging.yml")):
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)

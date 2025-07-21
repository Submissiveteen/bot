import logging

from logging.handlers import RotatingFileHandler

from pathlib import Path

import os

import yaml



def setup_logging():

    config_path = os.getenv("LOG_CONFIG", "config/logging.yml")

    log_file = Path("logs/deeplink.log")

    log_file.parent.mkdir(exist_ok=True)



    if os.path.exists(config_path):

        with open(config_path, 'r') as f:

            config = yaml.safe_load(f)

        logging.config.dictConfig(config)

    else:

        handler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=3)

        logging.basicConfig(level=logging.INFO, handlers=[handler])

import yaml
import logging.config
import os
from config import abspath

yaml_config_file = os.path.join(abspath, 'config/logging.yaml')
if os.path.exists(yaml_config_file):
    with open(yaml_config_file, 'r') as f:
        logging.config.dictConfig(yaml.safe_load(f))
else:
    logging.basicConfig(level="INFO")

logger = logging.getLogger("logger")
spiderLogger = logging.getLogger("spider")
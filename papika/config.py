import os
import logging
import logging.config
from typing import (
    Any,
    Dict,
)

import toml


log = logging.getLogger(__name__)

PAPIKA_CONFIG_ENV_VAR_NAME = 'PAPIKA_CONFIG'


def load_from_env_var_path(env_var_name: str = PAPIKA_CONFIG_ENV_VAR_NAME) -> Dict[str, Any]:
    if env_var_name not in os.environ:
        log.info("Environment variable '%s' not defined", env_var_name)
        raise ValueError("Config must be loaded from file specified in env var {0}".format(env_var_name))

    config_path = os.environ[env_var_name]
    if not os.path.isfile(config_path):
        raise ValueError("Could not load config from {0} because no such file exists".format(config_path))

    with open(config_path) as f:
        config = toml.load(f)

    if 'logging' in config:
        logging.config.dictConfig(config['logging'])
        log.info("Configured logging config from config file")

    return config

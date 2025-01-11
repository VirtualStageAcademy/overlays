import os
from typing import Any, Dict

import yaml
from config_loader import get_environment_config


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml and environment"""
    try:
        # Load base config from YAML
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        # Override with environment config
        env_config = get_environment_config()
        config.update(env_config)

        return config

    except Exception as e:
        print(f"Error loading config: {e}")
        # Return environment config as fallback
        return get_environment_config()

import json
import logging
import os
from functools import lru_cache
from typing import Any, Dict, Optional
from collections.abc import MutableMapping

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@lru_cache()
def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration"""
    try:
        # Load .env file
        load_dotenv()
        
        # Get environment and prefix
        env = os.getenv('ACTIVE_ENVIRONMENT', 'development')
        prefix = {
            'development': 'DEV',
            'preview': 'PREVIEW',
            'production': 'PROD'
        }.get(env, 'DEV')
        
        print(f"Active environment: {env}")  # Debug print
        print(f"Using prefix: {prefix}")     # Debug print
        
        # Get actual values
        client_id = os.getenv(f'{prefix}_CLIENT_ID')
        client_secret = os.getenv(f'{prefix}_CLIENT_SECRET')
        redirect_uri = os.getenv(f'{prefix}_REDIRECT_URI')
        websocket_url = os.getenv(f'{prefix}_WEBSOCKET_URL')
        home_url = os.getenv(f'{prefix}_HOME_URL')
        
        print(f"Found client_id: {client_id}")       # Debug print
        print(f"Found redirect_uri: {redirect_uri}") # Debug print
        
        # Build config object
        config: Dict[str, Any] = {
            'env_prefix': prefix,
            'environment': env,
            'zoom': {
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'websocket_url': websocket_url,
                'home_url': home_url
            }
        }
        
        print(f"Final config: {config}")  # Debug print
        return config
        
    except Exception as e:
        print(f"Config loader error: {str(e)}")  # Debug print
        raise

def load_env_vars(environment: str) -> Dict[str, str]:
    """Load environment variables based on active environment"""
    logging.info(f"Loading environment variables for: {environment}")
    # Map full environment names to prefixes
    env_prefix = {
        'development': 'DEV',
        'preview': 'PREVIEW',
        'production': 'PROD'
    }
    
    prefix = env_prefix.get(environment, 'DEV')
    logging.info(f"Using prefix: {prefix}")
    
    required_vars = [
        f'{prefix}_CLIENT_ID',
        f'{prefix}_CLIENT_SECRET',
        f'{prefix}_REDIRECT_URI',
        f'{prefix}_WEBSOCKET_URL',
        'TOKEN_ENCRYPTION_KEY',
        'SECRET_TOKEN',
        'VERIFICATION_TOKEN'
    ]
    
    env_vars = {
        'ACTIVE_ENVIRONMENT': environment,
    }
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        # Strip comments and whitespace
        value = value.split('#')[0].strip()
        # Strip environment prefix for consistency
        key = var.replace(f'{prefix}_', '') if var.startswith(prefix) else var
        env_vars[key] = value
    
    return env_vars

def load_yaml_config() -> Dict[str, Any]:
    """Load YAML configuration file"""
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        # Return empty dict if no YAML file exists
        return {}

def merge_configs(env_vars: Dict[str, str], yaml_config: Dict[str, Any], environment: str) -> Dict[str, Any]:
    """Merge environment variables with YAML config"""
    config = {
        'zoom': {
            'client_id': env_vars.get('CLIENT_ID'),
            'client_secret': env_vars.get('CLIENT_SECRET'),
            'redirect_uri': env_vars.get('REDIRECT_URI'),
            'websocket_url': env_vars.get('WEBSOCKET_URL'),
            'home_url': env_vars.get('HOME_URL')
        },
        'security': {
            'token_encryption_key': env_vars.get('TOKEN_ENCRYPTION_KEY'),
            'secret_token': env_vars.get('SECRET_TOKEN'),
            'verification_token': env_vars.get('VERIFICATION_TOKEN')
        },
        'environment': environment
    }
    
    # Only merge non-None values from YAML config
    if yaml_config:
        for section in config:
            if section in yaml_config:
                for key, value in yaml_config[section].items():
                    if value is not None and config[section].get(key) is None:
                        config[section][key] = value
    
    return config
def validate_config(config: Dict[str, Any]) -> None:
    """Validate the configuration structure and required fields"""
    required_fields = {
        'zoom': ['client_id', 'client_secret', 'redirect_uri', 'websocket_url'],
        'security': ['token_encryption_key', 'secret_token', 'verification_token'],
        'environment': None
    }
    
    for section, fields in required_fields.items():
        if section not in config:
            raise ValueError(f"Missing required section: {section}")
            
        if fields:  # If there are specific fields to check
            for field in fields:
                if field not in config[section]:
                    raise ValueError(f"Missing required field: {section}.{field}")
                if not config[section][field]:
                    raise ValueError(f"Empty required field: {section}.{field}")


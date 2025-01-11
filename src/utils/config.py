import os
import logging
from dotenv import load_dotenv
from src.config.config_loader import get_environment_config

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

def get_config():
    """Get configuration based on active environment"""
    try:
        logger.info("Getting config...")
        config = get_environment_config()
        logger.info(f"Config loaded: {config}")
        return config
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise

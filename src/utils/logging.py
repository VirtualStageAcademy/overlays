import logging
from typing import Optional

from flask import Flask


def setup_logging(app: Optional[Flask] = None, level: str = 'INFO') -> None:
    """Configure logging for the application"""
    # Set up basic configuration
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if app:
        # Add Flask handlers if app is provided
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        app.logger.addHandler(handler)
        app.logger.setLevel(getattr(logging, level))

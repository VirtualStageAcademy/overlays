import logging
from enum import Enum
from typing import Any, Dict

from ...config.config_loader import get_environment_config
from ...subscription.database import SubscriptionDB
from ..token_manager import TokenManager

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """Track WebSocket connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

class WebSocketHandler:
    """
    Handles WebSocket connections for overlays
    1. Manages Zoom WebSocket connection
    2. Handles overlay-specific events
    3. Maintains client connections
    """
    def __init__(self):
        self.config = get_environment_config()
        self.logger = logging.getLogger(__name__)
        self.token_manager = TokenManager()
        self.overlay_connections = {}  # Store overlay WS connections
        self.zoom_ws = None
        self._running = False
        self.subscription_db = SubscriptionDB()

    # ... (rest of the WebSocketHandler class methods) 
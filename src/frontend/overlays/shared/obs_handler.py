import json
import logging
from typing import Any, Dict

import websockets

from ....config.config_loader import get_environment_config

logger = logging.getLogger(__name__)

class OBSHandler:
    """
    Handles OBS WebSocket communication
    1. Manages OBS WebSocket connection
    2. Updates overlays based on Zoom events
    3. Handles OBS scene/source updates
    """
    def __init__(self):
        self.config = get_environment_config()
        self.obs_ws_url = "ws://localhost:4455"  # Default OBS WebSocket port
        self.obs_password = self.config.get('OBS_WEBSOCKET_PASSWORD')
        self.connected = False
        self.ws = None

    async def connect(self) -> bool:
        """Establish connection to OBS WebSocket"""
        try:
            self.ws = await websockets.connect(
                self.obs_ws_url,
                extra_headers={"Authorization": self.obs_password}
            )
            self.connected = True
            logger.info("Connected to OBS WebSocket")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to OBS: {e}")
            return False

    async def update_overlay(self, event_type: str, data: Dict[str, Any]):
        """Update OBS overlay based on event type"""
        if not self.connected:
            await self.connect()

        try:
            if event_type == 'chat_update':
                await self._update_chat_source(data)
            elif event_type == 'reaction_update':
                await self._update_reaction_source(data)
        except Exception as e:
            logger.error(f"Failed to update OBS overlay: {e}")

    async def _update_chat_source(self, data: Dict[str, Any]):
        """Update chat overlay source in OBS"""
        request = {
            'request-type': 'SetSourceSettings',
            'sourceName': 'ChatOverlay',
            'sourceSettings': {
                'text': f"{data['sender']}: {data['message']}"
            }
        }
        await self._send_obs_request(request)

    async def _update_reaction_source(self, data: Dict[str, Any]):
        """Update reaction overlay source in OBS"""
        request = {
            'request-type': 'SetSourceSettings',
            'sourceName': 'ReactionOverlay',
            'sourceSettings': {
                'text': f"{data['user']} reacted with {data['type']}"
            }
        }
        await self._send_obs_request(request)

    async def _send_obs_request(self, request: Dict[str, Any]):
        """Send request to OBS WebSocket"""
        try:
            await self.ws.send(json.dumps(request))
            response = await self.ws.recv()
            return json.loads(response)
        except Exception as e:
            logger.error(f"OBS request failed: {e}")
            self.connected = False
            raise 
import logging
from typing import Any, Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)

class ZoomAPI:
    """Handles Zoom API interactions"""
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user info from Zoom"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zoom.us/v2/users/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None 
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ....config.config_loader import get_environment_config
from ....server.token_manager import TokenManager
from ....subscription.database import SubscriptionDB

logger = logging.getLogger(__name__)

class OverlayManager:
    """
    Manages OBS overlay access and configurations
    1. Overlay URL generation
    2. Access validation
    3. WebSocket connection management
    """
    def __init__(self):
        self.config = get_environment_config()
        self.subscription_db = SubscriptionDB()
        self.token_manager = TokenManager()

    def get_overlay_urls(self, client_id: str) -> Dict[str, str]:
        """Generate overlay URLs with access token"""
        base_url = self.config['OVERLAY_BASE_URL']
        
        return {
            'chat': f"{base_url}/chat",
            'reactions': f"{base_url}/reactions",
            'participants': f"{base_url}/participants",
            'combined': f"{base_url}/combined"
        }

    async def validate_overlay_access(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate overlay access request"""
        try:
            # Verify token and get client info
            token_data = await self.token_manager.verify_token(token)
            if not token_data:
                return None

            # Check subscription status
            subscription = await self.subscription_db.get_subscription(token_data['client_id'])
            if not subscription or not self._is_subscription_active(subscription):
                return None

            return {
                'client_id': token_data['client_id'],
                'subscription': subscription
            }

        except Exception as e:
            logger.error(f"Overlay access validation failed: {e}")
            return None

    def _is_subscription_active(self, subscription: Dict[str, Any]) -> bool:
        """Check if subscription is active"""
        now = datetime.now()
        return now <= subscription['expiry_date'] 
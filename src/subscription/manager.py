import datetime
import logging
from typing import Any, Dict

from ..config.config_loader import get_environment_config
from ..utils.error_handler import handle_error
from .database import SubscriptionDB

logger = logging.getLogger(__name__)

class SubscriptionManager:
    """
    Handles subscription validation and renewal
    1. Subscription status checks
    2. Renewal management
    3. Grace period handling
    """
    def __init__(self):
        self.config = get_environment_config()
        self.subscription_db = SubscriptionDB()

    async def validate_access(self, user_id: str) -> Dict[str, Any]:
        """Validate user's subscription status"""
        try:
            subscription = await self.subscription_db.get_subscription(user_id)
            
            if not subscription:
                return {
                    'status': 'no_subscription',
                    'redirect_url': f"/checkout?user_id={user_id}"
                }

            now = datetime.now()
            if now <= subscription['expiry_date']:
                return {'status': 'active'}
            
            if now <= subscription['grace_period_end']:
                days_left = (subscription['grace_period_end'] - now).days
                return {
                    'status': 'grace_period',
                    'days_left': days_left,
                    'redirect_url': f"/renew?user_id={user_id}"
                }

            return {
                'status': 'expired',
                'redirect_url': f"/renew?user_id={user_id}"
            }

        except Exception as e:
            logger.error(f"Subscription validation failed: {e}")
            return {'status': 'error', 'message': str(e)} 
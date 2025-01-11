import asyncio
import base64
import logging
from datetime import datetime, timezone
from typing import Any, Dict

import aiohttp

from ..config.config_loader import get_environment_config

logger = logging.getLogger(__name__)

class TokenManager:
    _instance = None
    _tokens = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.config = get_environment_config()
            self._initialized = True
            self.logger.info("TokenManager initialized")

    def setup_environment(self):
        """Setup environment-specific configurations"""
        if not self.env:
            raise ValueError("ACTIVE_ENVIRONMENT must be set")
        
        # Use the nested config structure
        self.client_id = self.config['zoom']['client_id']
        self.client_secret = self.config['zoom']['client_secret']
        self.redirect_uri = self.config['zoom']['redirect_uri']

    async def get_tokens(self, code: str) -> dict:
        """Exchange code for tokens"""
        try:
            token_url = 'https://zoom.us/oauth/token'
            auth_str = base64.b64encode(
                f"{self.config['zoom']['client_id']}:{self.config['zoom']['client_secret']}".encode()
            ).decode()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    token_url,
                    headers={
                        'Authorization': f'Basic {auth_str}',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    data={
                        'grant_type': 'authorization_code',
                        'code': code,
                        'redirect_uri': self.config['zoom']['redirect_uri']
                    }
                ) as response:
                    if response.status == 200:
                        tokens = await response.json()
                        tokens['created_at'] = datetime.now().timestamp()
                        return tokens
                    else:
                        self.logger.error(f"Token exchange failed: {await response.text()}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error getting tokens: {e}")
            return None

    async def save_tokens(self, tokens: dict):
        """Save tokens to memory"""
        try:
            if not tokens or not isinstance(tokens, dict):
                self.logger.error("Invalid tokens provided")
                return False
                
            self._tokens = tokens
            self.logger.info(f"Tokens saved successfully: {bool(tokens.get('access_token'))}")
            self.logger.info(f"Current tokens: {bool(self._tokens)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving tokens: {e}")
            return False

    async def get_token(self):
        """Get current access token"""
        return self._tokens.get('access_token')

    async def refresh_token(self):
        """Refresh the access token"""
        # Implementation here
        pass

    async def get_valid_token(self):
        """Get a valid access token"""
        try:
            self.logger.info(f"Checking tokens: {bool(self._tokens)}")
            
            if not self._tokens:
                self.logger.error("No tokens stored")
                return None

            token = self._tokens.get('access_token')
            self.logger.info(f"Token retrieval: exists={bool(token)}")
            
            if token:
                self.logger.info("Found valid token")
                return token
                
            self.logger.warning("No valid token found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting valid token: {e}")
            return None

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        import base64
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode('ascii')
        base64_auth = base64.b64encode(auth_bytes).decode('ascii')
        return {
            "Authorization": f"Basic {base64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _is_token_expired(self, tokens: Dict[str, Any]) -> bool:
        """
        Check if the current token is expired or about to expire
        Includes a buffer time to prevent edge cases
        """
        try:
            # Get current timestamp
            now = datetime.now(timezone.utc).timestamp()
            
            # Get token creation time
            created_at = tokens.get('created_at', now)
            
            # Get token expiration (default 1 hour for Zoom)
            expires_in = tokens.get('expires_in', 3600)
            
            # Calculate expiration with buffer
            expiration_time = created_at + expires_in - self.token_buffer
            
            # Check if current time is past expiration
            is_expired = now >= expiration_time
            
            if is_expired:
                logger.info("Token requires refresh")
            
            return is_expired

        except Exception as e:
            logger.error(f"Error checking token expiration: {e}")
            return True  # Assume expired on error for safety

    async def start_refresh_scheduler(self, initial_tokens: Dict[str, Any]):
        """Start token refresh scheduling"""
        self._tokens = initial_tokens
        
        # Cancel existing refresh task if any
        if self.refresh_task:
            self.refresh_task.cancel()
            
        # Calculate time until next refresh
        refresh_in = self._get_refresh_time()
        
        # Schedule refresh
        self.refresh_task = asyncio.create_task(
            self._schedule_refresh(refresh_in)
        )
        logger.info(f"Token refresh scheduled in {refresh_in} seconds")

    async def _schedule_refresh(self, delay: int):
        """Schedule token refresh with delay"""
        try:
            await asyncio.sleep(delay)
            new_tokens = await self.refresh_token(self._tokens['refresh_token'])
            
            if new_tokens:
                self._tokens = new_tokens
                await self.save_tokens(new_tokens)
                # Schedule next refresh
                refresh_in = self._get_refresh_time()
                self.refresh_task = asyncio.create_task(
                    self._schedule_refresh(refresh_in)
                )
            else:
                logger.error("Token refresh failed")
                
        except asyncio.CancelledError:
            logger.info("Token refresh task cancelled")
        except Exception as e:
            logger.error(f"Refresh scheduling error: {e}")

    def _get_refresh_time(self) -> int:
        """Calculate time until next refresh needed"""
        now = datetime.now(timezone.utc).timestamp()
        created_at = self._tokens.get('created_at', now)
        expires_in = self._tokens.get('expires_in', 3600)
        
        # Refresh at buffer time before expiration
        refresh_at = created_at + expires_in - self.token_buffer
        
        # Calculate delay in seconds
        delay = max(0, refresh_at - now)
        return int(delay)

    async def handle_refresh_failure(self) -> bool:
        """Handle token refresh failures with retry logic"""
        try:
            self.refresh_attempt += 1
            logger.warning(f"Token refresh attempt {self.refresh_attempt}/{self.max_refresh_attempts}")

            if self.refresh_attempt >= self.max_refresh_attempts:
                logger.error("Max refresh attempts reached")
                # Notify OAuthServer of refresh failure
                await self._notify_refresh_failure()
                return False

            # Exponential backoff between attempts
            delay = 2 ** self.refresh_attempt
            await asyncio.sleep(delay)
            
            # Attempt refresh again
            tokens = await self.refresh_token(self._tokens['refresh_token'])
            if tokens:
                self.refresh_attempt = 0  # Reset counter on success
                await self.save_tokens(tokens)
                return True

            return False

        except Exception as e:
            logger.error(f"Refresh failure handling error: {e}")
            return False

    async def _notify_refresh_failure(self):
        """Notify OAuthServer that re-authorization is needed"""
        try:
            # Emit event for OAuthServer
            event = {
                'type': 'token_refresh_failed',
                'message': 'Token refresh failed, re-authorization required'
            }
            await self.emit_event(event)
        except Exception as e:
            logger.error(f"Failed to notify of refresh failure: {e}")

    def needs_refresh(self):
        """Check if token needs refresh"""
        if not self._tokens:
            return True
        
        expires_in = self._tokens.get('expires_in', 0)
        created_at = self._tokens.get('created_at', 0)
        
        if not expires_in or not created_at:
            return True
            
        now = datetime.now().timestamp()
        return (created_at + expires_in - 300) < now  # Refresh 5 minutes early

def get_stored_token():
    """Get the most recently stored access token"""
    try:
        # Get from global tokens if available
        if 'tokens' in globals() and globals()['tokens'].get('access_token'):
            return globals()['tokens']['access_token']
            
        print("No token found in memory")
        return None
        
    except Exception as e:
        print(f"Error getting token: {e}")
        return None


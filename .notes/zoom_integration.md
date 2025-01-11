# Zoom Integration Guidelines (2024-2025)

## OAuth App Configuration

### 1. App Setup
```json
{
    "oauth_app_type": "User-managed",
    "app_type": "Account-level app",
    "required_scopes": [
        "meeting:read",
        "meeting:write",
        "webinar:read",
        "webinar:write",
        "websocket"
    ],
    "redirect_urls": {
        "development": "https://{ngrok-url}/oauth/callback",
        "production": "https://overlays.virtualstageacademy.io/oauth/callback"
    }
}
```

### 2. Security Requirements
- Secure token storage with encryption
- State parameter validation
- PKCE (Proof Key for Code Exchange) implementation
- Regular token refresh handling

## Implementation Details

### 1. OAuth Flow
```python
class OAuthServer:
    def __init__(self):
        self.config = ConfigLoader().load()
        self.token_manager = TokenManager()
        self.websocket_handler = WebSocketHandler()
        
    async def initialize_oauth_flow(self):
        """Start OAuth flow with proper scopes and state parameter"""
        state = generate_secure_state()
        auth_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={self.config.client_id}&redirect_uri={self.config.redirect_uri}&state={state}"
        return auth_url, state
```

### 2. WebSocket Integration
- **Connection URL:** `wss://ws.zoom.us/ws`
- **Headers Required:**
  ```json
  {
    "Authorization": "Bearer {access_token}",
    "Client-Version": "2.12.0"
  }
  ```
- **Connection Management:**
  - Ping Interval: 20 seconds
  - Ping Timeout: 10 seconds
  - Auto-reconnect enabled

### 3. Error Handling
```python
class WebSocketHandler:
    async def handle_connection_error(self, error):
        """Handle common WebSocket errors"""
        if isinstance(error, WebSocketError4700):
            # Token validation failed
            await self.token_manager.refresh_token()
            await self.reconnect()
        elif isinstance(error, ConnectionError):
            # Connection lost
            await self.implement_backoff_retry()
```

## Development Setup

### 1. Local Testing
```bash
# Start local server
python oauth_server.py

# Start ngrok tunnel
ngrok http 5000

# Update .env with new ngrok URL
DEV_REDIRECT_URI=https://{ngrok-url}/oauth/callback
```

### 2. Verification Endpoints
- OAuth Status: `/oauth/status`
- OAuth Callback: `/oauth/callback`
- WebSocket Status: `/ws/status`
- Health Check: `/health`

## Production Deployment

### 1. Environment Configuration
```json
{
    "PROD_CLIENT_ID": "zoom_client_id",
    "PROD_CLIENT_SECRET": "zoom_client_secret",
    "PROD_REDIRECT_URI": "https://overlays.virtualstageacademy.io/oauth/callback",
    "PROD_WEBSOCKET_URL": "wss://ws.zoom.us/ws"
}
```

### 2. Security Headers
```python
headers = {
    'Strict-Transport-Security': 'max-age=31536000',
    'X-Content-Type-Options': 'nosniff',
    'Content-Security-Policy': "default-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}
```

## Troubleshooting Guide

### Common Issues

1. **WebSocket Error 4700**
   - Verify OAuth scopes
   - Check token validity
   - Validate WebSocket URL
   - Confirm proper headers

2. **Token Management**
   - Implement proper refresh flow
   - Handle token expiration
   - Secure storage implementation

3. **Connection Stability**
   - Monitor ping/pong
   - Implement reconnection logic
   - Handle connection timeouts

## Best Practices

1. **Security**
   - Implement PKCE
   - Validate state parameter
   - Secure token storage
   - Regular security audits

2. **Performance**
   - Connection pooling
   - Error rate monitoring
   - Bandwidth optimization
   - Cache management

3. **Monitoring**
   - Log all OAuth flows
   - Track WebSocket stability
   - Monitor error rates
   - Performance metrics 
# Development Guidelines

## Environment Setup

### 1. Virtual Environments
```bash
# Production Environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Configuration Setup
```bash
# Copy example environment file
cp .env.example .env

# Required environment variables (see zoom_integration.md for details)
DEV_CLIENT_ID=your_client_id
DEV_CLIENT_SECRET=your_client_secret
DEV_REDIRECT_URI=https://your-ngrok-url.ngrok-free.app/oauth/callback
DEV_WEBSOCKET_URL=wss://ws.zoom.us/ws
```

### 3. ngrok Configuration
```bash
# Start ngrok
ngrok http 5000

# Update .env with new ngrok URL and verify in zoom_integration.md
DEV_REDIRECT_URI=https://new-ngrok-url.ngrok-free.app/oauth/callback
```

### 4. Session Management
```bash
# Start development session
!startsession

# End development session and update documentation
!endsession
```

## Development Workflow

### 1. Code Organization
- Core application code in `src/server` directory
  - `oauth_server.py` - Main server entry point
  - `websocket_handler.py` - WebSocket functionality
  - `token_manager.py` - Token handling
  - `config_loader.py` - Configuration management
- Tests and development tools in `/tests`
- Configuration files in project root
- Documentation in `.notes`

### 2. Configuration Management
```python
# Loading configuration (see zoom_integration.md for required fields)
from src.config.config_loader import get_environment_config

config = get_environment_config()
zoom_client_id = config['zoom']['client_id']
```

### 3. Testing Protocol
```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
python -m src.server.oauth_server

# Run tests
python -m pytest tests/
```

## Security Guidelines

### 1. Environment Variables
- Never commit `.env` files
- Use environment prefixes consistently (DEV_, PREVIEW_, PROD_)
- Strip comments from production values
- Validate all required fields (see zoom_integration.md)

### 2. OAuth Testing
- Use ngrok for local OAuth testing
- Update Zoom App configuration with ngrok URL
- Never use production credentials in development
- Rotate test credentials regularly
- Follow security requirements in zoom_integration.md

### 3. Security Headers
```python
# Required security headers (see zoom_integration.md)
headers = {
    'Strict-Transport-Security': 'max-age=31536000',
    'X-Content-Type-Options': 'nosniff',
    'Content-Security-Policy': "default-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}
```

## Troubleshooting

### 1. Common Issues
- Missing environment variables
- Invalid ngrok configuration
- Security header validation failures
- OAuth callback errors
- WebSocket connection error 4700 (see zoom_integration.md)

### 2. Debug Tools
```python
# Debug configuration
print(f"Environment: {config['environment']}")
print(f"Redirect URI: {config['zoom']['redirect_uri']}")

# Test configuration
python test_config.py
```

### 3. Support Resources
- Zoom App documentation
- ngrok documentation
- Project documentation in `.notes`:
  - project_overview.md
  - zoom_integration.md
  - config_overview.md
- Team communication channels

# Development Tools
- Use end_session.py for systematic documentation updates
- Follow prompted steps for comprehensive session closure
- Verify all core documentation is updated
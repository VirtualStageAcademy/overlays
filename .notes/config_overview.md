# Configuration System Overview

## Environment Variables

### Prefix System
```
Development:  DEV_*
Preview:      PREVIEW_*
Production:   PROD_*
```

### Required Variables
```python
required_vars = [
    f'{prefix}_CLIENT_ID',        # Zoom OAuth Client ID
    f'{prefix}_CLIENT_SECRET',    # Zoom OAuth Client Secret
    f'{prefix}_REDIRECT_URI',     # OAuth callback URL
    f'{prefix}_WEBSOCKET_URL',    # WebSocket endpoint
    'TOKEN_ENCRYPTION_KEY',       # Encryption key for tokens
    'SECRET_TOKEN',              # App secret token
    'VERIFICATION_TOKEN'         # Zoom verification token
]
```

### Configuration Structure
```python
config = {
    'zoom': {
        'client_id': '...',
        'client_secret': '...',
        'redirect_uri': '...',
        'websocket_url': '...',
        'home_url': '...'
    },
    'security': {
        'token_encryption_key': '...',
        'secret_token': '...',
        'verification_token': '...'
    },
    'environment': 'development|preview|production'
}
```

## Configuration Sources

### 1. Environment Variables
- Primary source for sensitive data
- Environment-specific prefixes
- Automatic comment stripping
- Required field validation

### 2. YAML Configuration
- Secondary configuration source
- Non-sensitive default values
- Environment-specific overrides
- Located in `config.yaml`

## Security Features
- Automatic comment stripping from values
- Required field validation
- Environment-specific validation
- Security header enforcement

## Development Tools
- Test environment in `/tests/development/`
- ngrok integration for OAuth testing
- Separate test virtual environment
- Configuration validation tools 

## Dynamic Configuration Management
- **Runtime Changes:** Methods for managing configuration changes dynamically at runtime without service interruption.

## Security Enhancements
- **Updated Best Practices:** Latest best practices for OAuth security, data encryption, and secure handling of sensitive information. 
# Project Overview: Virtual Stage Academy (VSA)
**Version:** 1.8  
**Date:** January 9th, 2025 (AEST)  

## Project Vision
The Virtual Stage Academy (VSA) platform integrates Zoom meetings with dynamic OBS overlays, enhancing live webinars and audience engagement through real-time interaction, with subscription-based access control.

## Goals
1. Enable seamless integration with Zoom through OAuth and WebSocket.
2. Provide customizable, dynamic overlays for live streaming.
3. Empower users with tools to manage and analyze live events.
4. Manage user access through subscription-based authentication.

## Key Features
- **Zoom Integration:** OAuth 2.0-based authentication and real-time WebSocket communication.
- **Dynamic Overlays System:**
  - Chat overlay with customizable styling
  - Reaction animations with configurable effects
  - Interactive word cloud visualization
  - World map engagement tracker
  - Configurable countdown timer
  - All overlays individually controllable via Stream Deck
- **Deployment:** Built using Flask, hosted on Vercel, and integrated with OBS.
- **Subscription Management:**
  - Monthly and yearly subscription options
  - 10-day grace period for expired subscriptions
  - Automated renewal notifications
  - Subscription status checking before OAuth/WebSocket access

## Architecture Overview
1. **Backend:** 
   - Flask application for managing OAuth, WebSocket events, and API endpoints
     - `OAuthServer`: Handles Zoom authentication flow and token management
     - `TokenManager`: Manages token storage, refresh, and validation
     - `WebSocketHandler`: Manages real-time communication with Zoom
   - PostgreSQL database for user and subscription management
2. **Frontend:** 
   - Integration with OBS for live overlays
   - Modular overlay system with independent components:
     - `chat_overlay.js`
     - `reactions_overlay.js`
     - `word_cloud.js`
     - `world_map.js`
     - `countdown.js`
   - Stream Deck integration for overlay control
   - be creative to come up with other overlay ideas to add here like a dynamic yes/no poll, competition spinning with names of all attendees, plus other overlays that dont come from the app but are front end overlays hosted on vercel like timers and other useful overlays for presentations.
3. **Deployment:** 
   - Hosted on Vercel with environment-specific configurations
   - Stripe integration for payment processing

## Zoom Integration Details (2024-2025)
[Detailed Zoom integration specifications and guidelines are available in `.notes/zoom_integration.md`]

## Sample User Journey
1. User purchases subscription (monthly/yearly)
2. User authorizes the app via Zoom OAuth
3. System validates subscription status
4. App establishes a WebSocket connection for live event updates
5. OBS overlays are updated dynamically based on user interactions

## Future Implementation (Phase 2)
- **Subscription Database:**
  - User profiles and subscription details
  - Payment history and renewal tracking
  - Grace period management

- **Payment Integration:**
  - Stripe payment processing
  - Automatic renewal handling
  - Failed payment recovery

- **Access Control:**
  - Subscription status validation
  - Grace period enforcement
  - Renewal redirect flow

- **Enhanced Overlay System:**
  - Custom theme builder with visual editor
  - Overlay preset management and sharing
  - Analytics dashboard for engagement metrics
  - Additional overlay types:
    - Poll results visualization
    - Live announcements with animations
    - Custom branding overlays
    - Social media integration
    - Multi-language support

- **Stream Deck Integration:**
  - Custom profile templates
  - One-click scene switching
  - Overlay combination presets
  - Quick theme switching
  - Timer control shortcuts

- **Performance Optimization:**
  - WebSocket connection pooling
  - Asset preloading for overlays
  - Caching for frequently used data
  - Bandwidth optimization for world map

## Current Status
- **In Progress:** 
  - Overlay system testing
  - Stream Deck profile development
  - Theme customization system

- **Completed:** 
  - OAuth setup
  - WebSocket integration
  - Core overlay implementations:
    - Chat display
    - Reaction animations
    - Word cloud
    - World map
    - Countdown timer

- **Planned:** 
  - Analytics system
  - Theme editor
  - Preset management
  - Sound effects library

## Technical Implementation

### OAuth Flow
1. **Server Initialization:**
   ```python
   class OAuthServer:
       def __init__(self):
           self.config = get_environment_config()
           self.token_manager = TokenManager()
           self.ws_handler = WebSocketHandler()
   ```
   - Loads environment configuration
   - Initializes TokenManager for secure storage
   - Sets up WebSocketHandler for real-time events

2. **Authorization Process:**
   ```python
   async def handle_oauth_callback(self, code: str):
       tokens = await self.get_tokens(code)
       self.token_manager.save_tokens(tokens)
       await self.ws_handler.initialize_connection()
   ```
   - Receives OAuth callback code
   - Exchanges code for access tokens
   - Stores tokens securely
   - Initializes WebSocket connection

3. **Overlay System Integration:**
   - Each overlay connects via WebSocket
   - Real-time updates through event system
   - Independent configuration via URL parameters:
     ```
     https://your-domain.com/overlays/chat_overlay.html?token=ACCESS_TOKEN
     https://your-domain.com/overlays/reactions_overlay.html?token=ACCESS_TOKEN
     https://your-domain.com/overlays/word_cloud_overlay.html?token=ACCESS_TOKEN
     https://your-domain.com/overlays/world_map_overlay.html?token=ACCESS_TOKEN
     https://your-domain.com/overlays/countdown_overlay.html?duration=5&theme=default
     ```

4. **File Structure:**
   ```
   /src/server/
   ├── oauth_server.py      # OAuth flow and initialization
   ├── token_manager.py     # Token storage and refresh
   └── websocket_handler.py # Real-time communication
   
   /overlays/
   ├── shared/             # Shared overlay components
   ├── chat/              # Chat overlay system
   ├── reactions/         # Reaction animations
   ├── word_cloud/       # Word cloud visualization
   ├── world_map/        # Geographic engagement
   └── countdown/        # Configurable timer
   ```

### Configuration System
1. **Environment Management:**
   ```python
   def get_environment_config():
       active_env = os.getenv('ACTIVE_ENVIRONMENT', 'development')
       env_vars = load_env_vars(active_env)
       yaml_config = load_yaml_config()
       config = merge_configs(env_vars, yaml_config, active_env)
       validate_config(config)
       return config
   ```
   - Supports development, preview, and production environments
   - Environment-specific variable prefixing (DEV_, PREVIEW_, PROD_)
   - Automatic validation and security checks

2. **Development Infrastructure:**
   - Separate test environment in `/tests/development/`
   - Development server with required security headers:
     ```python
     @app.after_request
     def add_security_headers(response):
         response.headers['Strict-Transport-Security'] = 'max-age=31536000'
         response.headers['X-Content-Type-Options'] = 'nosniff'
         response.headers['Content-Security-Policy'] = "default-src 'self'"
         response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
     ```
   - ngrok integration for OAuth testing

3. **Virtual Environment Structure:**
   ```
   /venv/                  # Production dependencies
   /tests/
   ├── development/       # Development server and tools
   └── venv/             # Testing dependencies
   ```

4. **Configuration Validation:**
   - Automatic stripping of comments from values
   - Required field validation
   - Environment-specific URL validation
   - Security header compliance checks

### Known Issues
- WebSocket connection error 4700 persists despite:
  - Correct OAuth scopes (meeting:read, meeting:write, webinar:read, webinar:write, websocket)
  - Valid token storage
  - Proper WebSocket URL configuration
  - State parameter implementation
  
This issue needs further investigation with Zoom support.

## Error Handling
- **WebSocket Error 4700:** Detailed troubleshooting steps for resolving common WebSocket errors, including error 4700.

## Future Enhancements
- **Timeline and Dependencies:** Detailed planning for future enhancements with estimated timelines and dependencies.

## User Feedback Integration
- **Feedback Loop:** Process for integrating user feedback into development cycles to ensure alignment with user needs.
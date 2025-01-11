# Virtual Stage Academy TechHub Directory Structure

## Source Code (src/)
### Server Components
- `src/server/`
  - `oauth_server.py`         # Main server entry point and OAuth flow handler
  - `token_manager.py`        # Secure token storage and refresh handling
  - `zoom_api.py`            # Zoom API integration and requests
  - `webhook_meetings.json`   # Webhook data
  - `websocket/`             # WebSocket components
    - `handler.py`           # WebSocket implementation
    - `routes.py`            # WebSocket routes
    - `ws_handler.py`        # WebSocket specific handlers

### Configuration
- `src/config/`
  - `config_loader.py`        # Environment and configuration management
  - `config.yaml`            # Base configuration settings
  - `check_env.py`           # Environment validation utility
  - `test_config.py`         # Configuration tests
  - `tokens.json`            # Token storage

### Frontend Overlays
- `src/frontend/overlays/`
  - `shared/`                # Shared overlay components
    - `base.html`            # Base template
    - `obs_handler.py`       # OBS Studio integration
    - `overlay_handler.py`   # Overlay request processing
    - `overlay_manager.py`   # Overlay business logic
    - `overlay_client.js`    # Client-side overlay script
    - `styles.css`           # Shared styles
  - `chat/`                  # Chat overlay
    - `chat.html`
    - `chat.css`
    - `chat.js`
  - `reactions/`             # Reactions overlay
    - `reactions.html`
    - `reactions.css`
    - `reactions.js`
  - `word_cloud/`           # Word cloud overlay
    - `word_cloud.html`
    - `word_cloud.css`
    - `word_cloud.js`
  - `world_map/`            # World map overlay
    - `world_map.html`
    - `world_map.css`
    - `world_map.js`
  - `countdown/`            # Countdown overlay
    - `countdown.html`
    - `countdown.css`
    - `countdown.js`

### Subscription System
- `src/subscription/`
  - `database.py`           # Database handlers
  - `manager.py`            # Subscription management
  - `migrations/`           # Database migrations
    - `create_subscriptions.sql`

### Utils
- `src/utils/`
  - `config.py`            # Configuration utilities
  - `error_handler.py`     # Error handling
  - `file_finder.py`       # File system utilities
  - `logging.py`           # Logging setup

## Tests
- `tests/`
  - `integration/`         # Integration tests
    - `test_oauth_integration.py`
    - `test_oauth_errors.py`
    - `test_oauth_cleanup.py`
    - `test_oauth_with_mock_db.py`
    - `test_subscription_integration.py`
    - `test_websocket_server.py`
  - `mocks/`              # Test mocks
    - `mock_database.py`
  - `test_oauth_server.py`

## Project Documentation
- `.notes/`               # Project documentation
  - `project_overview.md`
  - `task_list.md`
  - `meeting_notes.md`
  - `directory_structure.md`
  - `config_overview.md`
  - `development_guidelines.md`
  - `zoom_integration.md`
  - `custom_instructions.json`
  - `dev_tools/`
    - `init_session.sh`
    - `session_init.py`
    - `end_session.sh`
    - `end_session.py`
    - `aliases.sh`

## Configuration Files
- `.env`                 # Environment variables (not in git)
- `.env.backup`          # Environment backup
- `.env.example`         # Environment template
- `.cursorrules`         # AI assistant rules
- `.cursorignore`        # Cursor ignore rules
- `.gitignore`           # Git ignore rules
- `.vercelignore`        # Vercel ignore rules
- `vercel.json`          # Vercel deployment configuration
- `requirements.txt`     # Python dependencies
- `run.py`              # Main entry point
- `README.md`           # Project readme

## Deployment
- `.vercel/`            # Vercel deployment files
  - `project.json`
  - `org.json`
  - `README.txt`

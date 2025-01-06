import os
import logging
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
from base64 import b64encode
import requests
from token_manager import save_tokens, load_tokens, refresh_access_token  # Token management functions
from websocket_handler import WebSocketHandler  # WebSocket handler
from config_loader import get_environment_config  # Environment configuration loader

# ==========================
# Set up Logging
# ==========================
# Configure logging to help in debugging and tracking the flow of the application.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================
# Load Environment Variables
# ==========================
# Essential for accessing environment-specific configurations.
try:
    load_dotenv()  # Load variables from .env
    print("DEBUG: .env file loaded successfully.")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Debug: Verify if environment variables are loaded
print({
    "ACTIVE_ENVIRONMENT": os.getenv("ACTIVE_ENVIRONMENT"),
    "DEV_CLIENT_ID": os.getenv("DEV_CLIENT_ID"),
    "DEV_CLIENT_SECRET": os.getenv("DEV_CLIENT_SECRET"),
    "DEV_REDIRECT_URI": os.getenv("DEV_REDIRECT_URI"),
    "DEV_HOME_URL": os.getenv("DEV_HOME_URL"),
    "DEV_WEBSOCKET_URL": os.getenv("DEV_WEBSOCKET_URL"),
})

# ==========================
# Helper: Load Environment Settings
# ==========================
# Dynamically loads settings based on the active environment to configure the application.
def load_environment_settings():
    """
    Dynamically load environment-specific settings.
    This ensures the application uses the correct environment variables
    based on ACTIVE_ENVIRONMENT (e.g., development, preview, production).
    """
    # Retrieve the active environment from .env or default to 'development'
    active_env = os.getenv("ACTIVE_ENVIRONMENT", "development")
    prefix = active_env.upper()[:3]  # Get the first three letters, e.g., DEV, PRE, or PRO

    # Debug: Check the active environment prefix
    print(f"DEBUG: Active environment prefix is {prefix}")

    # ==========================
    # Retrieve settings from environment variables
    # ==========================
    settings = {}
    required_vars = ["CLIENT_ID", "CLIENT_SECRET", "REDIRECT_URI", "HOME_URL", "WEBSOCKET_URL"]

    for var in required_vars:
        full_key = f"{prefix}_{var}"  # Dynamically construct variable name
        settings[var.lower()] = os.getenv(full_key)  # Retrieve the value
        print(f"DEBUG: Attempting to load {full_key}: {settings[var.lower()]}")

    # ==========================
    # Validate Settings
    # ==========================
    # Ensures all required environment variables are loaded to avoid runtime errors.
    missing_vars = [key for key, value in settings.items() if value is None]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return settings

# ==========================
# Load and Log Settings
# ==========================
# Load environment-specific settings and log the active environment for debugging purposes.
env_settings = load_environment_settings()
logger.info(f"Active Environment: {os.getenv('ACTIVE_ENVIRONMENT', 'development')}")
logger.info(f"WebSocket URL: {env_settings['websocket_url']}")

# ==========================
# Flask App Initialization
# ==========================
# Initialize Flask application to handle incoming requests.
app = Flask(__name__)

# ==========================
# Security Headers Setup
# ==========================
# Applies security headers globally to enhance application security.
@app.after_request
def apply_security_headers(response):
    """
    Add security headers to all outgoing HTTP responses.
    Helps protect against common vulnerabilities like clickjacking, XSS, etc.
    """
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# ==========================
# Routes Definitions
# ==========================
# Define Flask routes to handle specific requests.

@app.route("/")
def home():
    """
    Root route to display a clickable link for Zoom authorization.
    Redirects the user to Zoom for app authorization.
    """
    zoom_auth_url = (
        f"https://zoom.us/oauth/authorize?"
        f"client_id={env_settings['client_id']}&"
        f"response_type=code&"
        f"redirect_uri={env_settings['redirect_uri']}"
    )
    return f'<a href="{zoom_auth_url}">Click here to authorize with Zoom</a>'

@app.route("/callback", methods=["GET"])
def callback():
    """
    OAuth callback route to exchange authorization code for tokens.
    After Zoom authorization, this route handles the token exchange process.
    """
    code = request.args.get("code")
    if not code:
        logger.error("Authorization code is missing.")
        return jsonify({"error": "Authorization code is missing"}), 400

    # Exchange the authorization code for access and refresh tokens
    token_url = "https://zoom.us/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": env_settings["redirect_uri"]
    }
    headers = {
        "Authorization": f"Basic {b64encode(f'{env_settings['client_id']}:{env_settings['client_secret']}'.encode()).decode()}"
    }

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code == 200:
        # Save tokens on successful response
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        save_tokens(access_token, refresh_token)  # Persist tokens securely
        logger.info("Access and refresh tokens saved successfully.")
        return jsonify({"message": "Authorization successful!"})
    else:
        # Log errors and return failure message
        logger.error(f"Failed to exchange code for tokens: {response.status_code} - {response.text}")
        return jsonify({"error": "Failed to obtain access token"}), 500

@app.route("/start_websocket", methods=["POST"])
def start_websocket():
    """
    Start the WebSocket connection using the current access token.
    This is essential for real-time interaction with Zoom events.
    """
    # Load stored tokens
    access_token, refresh_token = load_tokens()
    if not access_token or not refresh_token:
        logger.error("Missing access or refresh token. Please authorize the app first.")
        return jsonify({"error": "Missing access or refresh token. Authorize the app first."}), 400

    # Initialize WebSocket handler
    websocket_handler = WebSocketHandler({
        "websocket_url": f"{env_settings['websocket_url']}&access_token={access_token}"
    })

    try:
        websocket_handler.connect()
        return jsonify({"message": "WebSocket connection started successfully."})
    except Exception as e:
        # Log any exceptions and return error message
        logger.error(f"Failed to start WebSocket: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================
# Start Flask App
# ==========================
# Start the Flask server for handling incoming HTTP requests.
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

import os
import logging
from flask import Flask, request, jsonify, make_response, after_request
from dotenv import load_dotenv
from base64 import b64encode
import requests
from token_manager import save_tokens, load_tokens, refresh_access_token
from websocket_handler import WebSocketHandler
from config_loader import get_environment_config

# ==========================
# Set up Logging
# ==========================
# Configure logging to help in debugging and tracking flow of application.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================
# Load Environment Variables
# ==========================
# Essential for accessing environment-specific configurations.
load_dotenv()

# ==========================
# Helper: Load Environment Settings
# ==========================
# Dynamically loads settings based on the active environment to configure the application.
def load_environment_settings():
    active_env = os.getenv("ACTIVE_ENVIRONMENT", "development")
    prefix = active_env.upper()

    settings = {
        "client_id": os.getenv(f"{prefix}_CLIENT_ID"),
        "client_secret": os.getenv(f"{prefix}_CLIENT_SECRET"),
        "redirect_uri": os.getenv(f"{prefix}_REDIRECT_URI"),
        "home_url": os.getenv(f"{prefix}_HOME_URL"),
    }

    _, websocket_url = get_environment_config()
    settings["websocket_url"] = websocket_url

    return settings

env_settings = load_environment_settings()
logger.info(f"Active Environment: {os.getenv('ACTIVE_ENVIRONMENT', 'development')}")
logger.info(f"WebSocket URL: {env_settings['websocket_url']}")

# ==========================
# Flask App Initialization
# ==========================
app = Flask(__name__)

# ==========================
# Security Headers Setup
# ==========================
# Applies security headers to all responses to enhance security.
@app.after_request
def apply_security_headers(response):
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# ==========================
# Routes Definitions
# ==========================
# Define Flask routes to handle requests.
@app.route("/")
def home():
    """ Root route to display a clickable link for Zoom authorization. """
    zoom_auth_url = (
        f"https://zoom.us/oauth/authorize?"
        f"client_id={env_settings['client_id']}&"
        f"response_type=code&"
        f"redirect_uri={env_settings['redirect_uri']}"
    )
    return f'<a href="{zoom_auth_url}">Click here to authorize with Zoom</a>'

@app.route("/callback", methods=["GET"])
def callback():
    """ Handles the OAuth callback to exchange authorization code for tokens. """
    code = request.args.get("code")
    if not code:
        logger.error("Authorization code is missing.")
        return jsonify({"error": "Authorization code is missing"}), 400

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
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        save_tokens(access_token, refresh_token)
        logger.info("Access and refresh tokens saved successfully.")
        return jsonify({"message": "Authorization successful!"})
    else:
        logger.error(f"Failed to exchange code for tokens: {response.status_code} - {response.text}")
        return jsonify({"error": "Failed to obtain access token"}), 500

@app.route("/start_websocket", methods=["POST"])
def start_websocket():
    """ Starts the WebSocket connection using the current access token. """
    access_token, refresh_token = load_tokens()
    if not access_token or not refresh_token:
        logger.error("Missing access or refresh token. Please authorize the app first.")
        return jsonify({"error": "Missing access or refresh token. Authorize the app first."}), 400

    websocket_handler = WebSocketHandler({
        "websocket_url": f"{env_settings['websocket_url']}&access_token={access_token}"
    })

    try:
        websocket_handler.connect()
        return jsonify({"message": "WebSocket connection started successfully."})
    except Exception as e:
        logger.error(f"Failed to start WebSocket: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================
# Start Flask App
# ==========================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

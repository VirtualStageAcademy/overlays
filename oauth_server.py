import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from base64 import b64encode
import requests
from token_manager import save_tokens, load_tokens, refresh_access_token  # Token management functions
from websocket_handler import WebSocketHandler  # WebSocket handler

# ==========================
# Load Environment Variables
# ==========================
load_dotenv()

# ==========================
# Helper: Load Environment Settings
# ==========================
def load_environment_settings():
    active_env = os.getenv("ACTIVE_ENVIRONMENT", "development")
    prefix = active_env.upper()

    settings = {
        "client_id": os.getenv(f"{prefix}_CLIENT_ID"),
        "client_secret": os.getenv(f"{prefix}_CLIENT_SECRET"),
        "redirect_uri": os.getenv(f"{prefix}_REDIRECT_URI"),
        "websocket_url": os.getenv(f"{prefix}_WEBSOCKET_URL"),
        "home_url": os.getenv(f"{prefix}_HOME_URL"),
    }

    return settings

# Load environment-specific settings
env_settings = load_environment_settings()
print(f"[INFO] Active Environment: {os.getenv('ACTIVE_ENVIRONMENT', 'development')}")
print(f"[INFO] WebSocket URL: {env_settings['websocket_url']}")

# ==========================
# Flask App Initialization
# ==========================
app = Flask(__name__)

@app.route("/")
def home():
    """
    Root route to display a clickable link for Zoom authorization.
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
    """
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization code is missing"}), 400

    # Exchange the authorization code for access and refresh tokens
    token_url = "https://zoom.us/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": ZOOM_REDIRECT_URI
    }
    headers = {
        "Authorization": f"Basic {b64encode(f'{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}'.encode()).decode()}"
    }

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        save_tokens(access_token, refresh_token)  # Save tokens to file
        print("[INFO] Access and refresh tokens saved successfully.")
        return jsonify({"message": "Authorization successful!"})
    else:
        print(f"[ERROR] Failed to exchange code for tokens: {response.status_code} - {response.text}")
        return jsonify({"error": "Failed to obtain access token"}), 500

@app.route("/start_websocket", methods=["POST"])
def start_websocket():
    """
    Start the WebSocket connection using the current access token.
    """
    access_token, refresh_token = load_tokens()

    if not access_token or not refresh_token:
        return jsonify({"error": "Missing access or refresh token. Authorize the app first."}), 400

    # Initialize WebSocket handler
    websocket_url = config["websocket"][WEB_SOCKET_ENV]["url"]
    websocket_handler = WebSocketHandler({
        "environment": WEB_SOCKET_ENV,
        "websocket": {
            "url": f"{websocket_url}&access_token={access_token}"
        }
    })

    try:
        websocket_handler.connect()
        return jsonify({"message": "WebSocket connection started successfully."})
    except Exception as e:
        print(f"[ERROR] Failed to start WebSocket: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/refresh_tokens", methods=["POST"])
def refresh_tokens_route():
    """
    Route to manually refresh tokens if needed.
    """
    _, refresh_token = load_tokens()
    if not refresh_token:
        return jsonify({"error": "Missing refresh token. Authorize the app first."}), 400

    new_access_token, new_refresh_token = refresh_access_token(refresh_token)
    if new_access_token and new_refresh_token:
        save_tokens(new_access_token, new_refresh_token)
        return jsonify({"message": "Tokens refreshed successfully."})
    else:
        return jsonify({"error": "Failed to refresh tokens."}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

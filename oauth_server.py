import os  # To interact with environment variables
import re  # For emoji extraction
from flask import Flask, request, jsonify  # Flask utilities
from dotenv import load_dotenv  # To load .env variables
import yaml  # To load YAML configuration
from base64 import b64encode  # For encoding client credentials
import requests  # For making HTTP requests

# =======================
# Configuration Section
# =======================

# Load environment variables from .env file
load_dotenv()

# Load configuration from config.yaml
def load_config():
    config_path = "config.yaml"
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

# Load the configuration from YAML
config = load_config()

# Retrieve Environment and Config Variables
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ZOOM_REDIRECT_URI = config['zoom']['redirect_uri']
ZOOM_WEBHOOK_ENDPOINT = config['zoom']['webhook_endpoint']
ZOOM_SCOPES = config['zoom']['scopes']

# Debugging: Ensure variables are loaded
if not SECRET_TOKEN:
    raise EnvironmentError("ERROR: SECRET_TOKEN is missing! Check .env file.")
if not VERIFICATION_TOKEN:
    raise EnvironmentError("ERROR: VERIFICATION_TOKEN is missing! Check .env file.")

# Debug logs
print(f"DEBUG: SECRET_TOKEN loaded successfully.")
print(f"DEBUG: VERIFICATION_TOKEN loaded successfully.")
print(f"DEBUG: Zoom Redirect URI loaded from config.yaml: {ZOOM_REDIRECT_URI}")

# Initialize Flask app
app = Flask(__name__)

# =======================
# Middleware to Add OWASP Headers
# =======================
@app.after_request
def add_owasp_headers(response):
    """Add OWASP security headers to the response"""
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self';"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# =======================
# Utility Functions
# =======================
def extract_emojis(text):
    """Extract emojis from a given text message."""
    emoji_pattern = re.compile(
        "["  # Add Unicode ranges for emojis
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F700-\U0001F77F"  # Alchemical symbols
        "\U0001FA00-\U0001FAFF"  # Supplemental symbols
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.findall(text)

# =======================
# Flask Routes
# =======================
@app.route("/")
def home():
    """Default route to confirm the app is running."""
    return "OAuth App is Running!"

@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code', None)
    if code:
        # Exchange code for an access token
        token_url = "https://zoom.us/oauth/token"
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': ZOOM_REDIRECT_URI
        }
        headers = {
            'Authorization': 'Basic ' + b64encode(f"{os.getenv('ZOOM_CLIENT_ID')}:{os.getenv('ZOOM_CLIENT_SECRET')}".encode()).decode()
        }
        response = requests.post(token_url, data=payload, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            return jsonify({"access_token": tokens.get("access_token"), "refresh_token": tokens.get("refresh_token")}), 200
        else:
            return jsonify({"error": "Failed to obtain access token", "status": response.status_code}), response.status_code
    else:
        return jsonify({"error": "No code provided"}), 400

@app.route("/webhooks/notifications", methods=["POST"])
def handle_zoom_webhook():
    """Handles incoming Zoom webhook events."""
    try:
        token = request.headers.get("Authorization")
        if token != f"Bearer {SECRET_TOKEN}":
            return jsonify({"error": "Unauthorized"}), 401

        data = request.json or {}
        if "plainToken" in data:
            return jsonify({"plainToken": data["plainToken"]})

        if data.get("token") != VERIFICATION_TOKEN:
            return jsonify({"error": "Invalid Verification Token"}), 403

        event = data.get("event", "unknown_event")
        print(f"DEBUG: Received event: {event}")
    
        if event == "meeting.chat_message_sent":
            payload = data.get("payload", {}).get("object", {})
            message = payload.get("message", "")
            emojis = extract_emojis(message)
            print(f"DEBUG: Chat Message: {message}")
            print(f"DEBUG: Extracted Emojis: {emojis}")
        elif event == "reaction_added":
            payload = data.get("payload", {}).get("object", {})
            reaction = payload.get("reaction", "")
            participant = payload.get("participant", {})
            print(f"DEBUG: Reaction Added: {reaction}")
            print(f"DEBUG: Participant Details: {participant}")
        else:
            print(f"INFO: Unhandled event type: {event}")
        return jsonify({"message": "Event received"}), 200
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# =======================
# Main Execution
# =======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

import os  # For environment variables
import re  # For emoji extraction
import requests  # For Zoom API calls
from flask import Flask, request, jsonify, redirect  # Flask utilities
from dotenv import load_dotenv  # To load .env variables

# =======================
# Configuration Section
# =======================

# Define the path to the .env file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Load environment variables from .env file
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    print(f"DEBUG: Loaded environment variables from {ENV_PATH}")
else:
    raise FileNotFoundError(f"ERROR: Environment file not found at {ENV_PATH}")

# Retrieve environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")

# Ensure critical variables are loaded
required_vars = [CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SECRET_TOKEN, VERIFICATION_TOKEN]
for var in required_vars:
    if not var:
        raise EnvironmentError(f"ERROR: Missing required environment variable: {var}")

print("DEBUG: All required environment variables loaded successfully.")

# Initialize Flask app
app = Flask(__name__)

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

def exchange_code_for_tokens(auth_code):
    """Exchange authorization code for access and refresh tokens."""
    url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Basic {CLIENT_ID}:{CLIENT_SECRET}",
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()

# =======================
# Flask Routes
# =======================

@app.route("/")
def home():
    """Default route to confirm the app is running."""
    return "OAuth Server is Running!"

@app.route("/authorize")
def authorize():
    """Redirect the user to Zoom's authorization page."""
    zoom_auth_url = (
        f"https://zoom.us/oauth/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(zoom_auth_url)

@app.route("/callback")
def callback():
    """Handle Zoom's OAuth callback."""
    auth_code = request.args.get("code")
    if not auth_code:
        return jsonify({"error": "Authorization code is missing"}), 400

    try:
        tokens = exchange_code_for_tokens(auth_code)
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        print(f"DEBUG: Access Token: {access_token}")
        print(f"DEBUG: Refresh Token: {refresh_token}")
        return jsonify({"message": "Authorization successful", "tokens": tokens}), 200
    except Exception as e:
        print(f"ERROR: Failed to exchange code for tokens: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/webhooks/notifications", methods=["POST"])
def handle_zoom_webhook():
    """Handle incoming Zoom webhook events."""
    try:
        # Verify the request with Authorization header
        token = request.headers.get("Authorization")
        if token != f"Bearer {SECRET_TOKEN}":
            return jsonify({"error": "Unauthorized"}), 401

        # Parse incoming JSON data
        data = request.json or {}

        # Zoom's Challenge-Response Check
        if "plainToken" in data:
            return jsonify({"plainToken": data["plainToken"]})

        # Validate Verification Token
        if data.get("token") != VERIFICATION_TOKEN:
            return jsonify({"error": "Invalid Verification Token"}), 403

        # Process Events
        event = data.get("event", "unknown_event")
        print(f"DEBUG: Received event: {event}")

        if event == "meeting.chat_message_sent":
            # Process chat messages
            payload = data.get("payload", {}).get("object", {})
            message = payload.get("message", "")
            emojis = extract_emojis(message)
            print(f"DEBUG: Chat Message: {message}")
            print(f"DEBUG: Extracted Emojis: {emojis}")

        elif event == "reaction_added":
            # Process reactions
            payload = data.get("payload", {}).get("object", {})
            reaction = payload.get("reaction", "")
            participant = payload.get("participant", {})
            print(f"DEBUG: Reaction Added: {reaction}")
            print(f"DEBUG: Participant Details: {participant}")

        else:
            # Handle unhandled events
            print(f"INFO: Unhandled event type: {event}")

        return jsonify({"message": "Event received"}), 200

    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# =======================
# Main Execution
# =======================

if __name__ == "__main__":
    app.run(port=5000)

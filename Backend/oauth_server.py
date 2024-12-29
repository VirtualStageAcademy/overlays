import os  # To interact with environment variables
import re  # For emoji extraction
from flask import Flask, request, jsonify  # Flask utilities
from dotenv import load_dotenv  # To load .env variables

# =======================
# Configuration Section
# =======================

# Load environment variables from .env file
ENV_PATH = "/Users/craighubbard/Documents/VirtualStageAcademy/TechHub/Config/.env"
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    print(f"DEBUG: Loaded environment variables from {ENV_PATH}")
else:
    print(f"ERROR: Environment file not found at {ENV_PATH}")

# Retrieve environment variables
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")

# Debugging: Ensure variables are loaded
if not SECRET_TOKEN or not VERIFICATION_TOKEN:
    raise EnvironmentError("Missing essential environment variables! Check .env file.")

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

# =======================
# Flask Routes
# =======================

@app.route("/")
def home():
    """Default route to confirm the app is running."""
    return "Webhook App is Running!"

@app.route("/webhooks/notifications", methods=["POST"])
def handle_zoom_webhook():
    """Handles incoming Zoom webhook events."""
    try:
        # Verify the request with Authorization header
        token = request.headers.get("Authorization")
        if token != f"Bearer {SECRET_TOKEN}":
            print("ERROR: Unauthorized access attempt")
            return jsonify({"error": "Unauthorized"}), 401
        
        # Parse the incoming JSON data
        data = request.json or {}
        
        # Zoom's Challenge-Response Check
        if "plainToken" in data:
            print("DEBUG: Challenge-Response Received")
            return jsonify({"plainToken": data["plainToken"]})
        
        # Validate Verification Token
        if data.get("token") != VERIFICATION_TOKEN:
            print("ERROR: Verification token mismatch")
            return jsonify({"error": "Invalid Verification Token"}), 403
        
        # Process events
        event = data.get("event", "unknown_event")
        print(f"DEBUG: Received event: {event}")
        
        if event == "meeting.chat_message_sent":
            payload = data.get("payload", {}).get("object", {})
            message = payload.get("message", "")
            emojis = extract_emojis(message)
            print(f"Chat Message: {message}")
            print(f"Extracted Emojis: {emojis}")
        
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
    app.run(port=5000)

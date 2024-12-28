import requests
from flask import Flask, request, jsonify
import re  # For extracting emojis
from dotenv import load_dotenv
import os

# =======================
# Configuration Section
# =======================

# Load environment variables from .env file
load_dotenv()

# Debugging: Print loaded environment variables
print("DEBUG: Environment Variables Loaded")

# Retrieve environment variables
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")

# Initialize Flask app
app = Flask(__name__)

# =======================
# Utility Functions
# =======================

# Function to extract emojis from a text message (retain if needed for webhook events)
def extract_emojis(text):
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
    return "Webhook App is Running!"

@app.route("/webhooks/notifications", methods=["POST"])
def handle_zoom_webhook():
    """Handles incoming Zoom webhook events."""
    # Verify the request with Authorization header
    token = request.headers.get("Authorization")
    if token != f"Bearer {SECRET_TOKEN}":
        print("ERROR: Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    # Parse the incoming JSON data
    data = request.json

    # Zoom's Challenge-Response Check
    if "plainToken" in data:
        print("DEBUG: Challenge-Response Received")
        return jsonify({"plainToken": data["plainToken"]})

    # Validate Verification Token
    if data.get("token") != VERIFICATION_TOKEN:
        print("ERROR: Verification token mismatch")
        return jsonify({"error": "Invalid Verification Token"}), 403

    try:
        # Handle specific events
        event = data.get("event", "unknown_event")
        print(f"Received event: {event}")

        if event == "meeting.participant_joined":
            participant_data = data.get("payload", {}).get("object", {})
            user_name = participant_data.get("participant", {}).get("user_name", "Unknown")
            print(f"Participant Joined: {user_name}")

        elif event == "meeting.chat_message_sent":
            message = data.get("payload", {}).get("object", {}).get("message", "")
            emojis = extract_emojis(message)
            print(f"Chat Message: {message}")
            print(f"Emojis Extracted: {emojis}")

        else:
            print(f"Unhandled event type: {event}")

    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

    # Respond to Zoom that the event was received
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)

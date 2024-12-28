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
print("CLIENT_ID:", os.getenv("CLIENT_ID"))
print("CLIENT_SECRET:", os.getenv("CLIENT_SECRET"))
print("REDIRECT_URI:", os.getenv("REDIRECT_URI"))

# Retrieve environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Tokens
import os

SECRET_TOKEN = os.getenv("SECRET_TOKEN")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")

# Zoom API Endpoints
TOKEN_URL = "https://zoom.us/oauth/token"
CHAT_MESSAGES_URL = "https://api.zoom.us/v2/chat/users/me/messages"
AUTH_URL = f"https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

app = Flask(__name__)

# =======================
# Utility Functions
# =======================

# Function to extract emojis from a text message
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
    return f'<a href="{AUTH_URL}">Connect Your Zoom Account</a>'

@app.route("/oauth/callback")
def oauth_callback():
    auth_code = request.args.get("code")
    if not auth_code:
        return jsonify({"error": "Authorization code not provided"}), 400

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(
        TOKEN_URL,
        data=data,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )

    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve access token"}), response.status_code

    response_data = response.json()
    return jsonify({"access_token": response_data.get("access_token")})

@app.route("/zoom-data/<token>")
def get_zoom_data(token):
    try:
        # Make the request to Zoom API
        response = requests.get(
            "https://api.zoom.us/v2/chat/users/me/messages",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Debugging: Print response details
        print("DEBUG: Chat Messages API Response")
        print("Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Response Text:", response.text)

        # Handle non-200 status codes gracefully
        if response.status_code != 200:
            error_message = f"Failed to retrieve chat messages: {response.json().get('message', 'Unknown Error')}"
            print(f"ERROR: {error_message}")
            return jsonify({"error": error_message}), response.status_code

        # Process the messages and extract emojis
        chat_messages = response.json().get("messages", [])
        emojis = []
        for msg in chat_messages:
            message_text = msg.get("message", "")
            emojis.extend(extract_emojis(message_text))

        # Return the chat messages and extracted emojis
        return jsonify({
            "chat": [msg.get("message", "") for msg in chat_messages],
            "reactions": emojis
        })

    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        error_message = f"Network error: {str(e)}"
        print(f"ERROR: {error_message}")
        return jsonify({"error": error_message}), 500
    except Exception as e:
        # Catch-all for unexpected errors
        error_message = f"Unexpected error: {str(e)}"
        print(f"ERROR: {error_message}")
        return jsonify({"error": error_message}), 500


if __name__ == "__main__":
    app.run(port=5000)

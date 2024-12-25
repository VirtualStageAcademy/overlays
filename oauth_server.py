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
SECRET_TOKEN = "DVb8pCcSTteCwKPP2oxikA"
VERIFICATION_TOKEN = "a3VcjPvKRzOohwhg6CFlzQ"

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

@app.route("/zoom-data")
def get_zoom_data():
    # Updated token for testing
    token = "eyJzdiI6IjAwMDAwMiIsImFsZyI6IkhTNTEyIiwidiI6IjIuMCIsImtpZCI6IjU2NWViNWRjLTBiMGYtNDYxOC05ZGU0LTI1NjJlMTJhMmZmYSJ9.eyJ2ZXIiOjEwLCJhdWlkIjoiNzg5YzQ2NzAyNzU2NDUzYTgyNzQ2Yzk4N2YxZjY0ZjU5NzQwMTgxYTFiNGE2NmRjYjc0Mjk4N2QwYWQ3NzQxYiIsImNvZGUiOiJkTVNrMnpScmJrWVcwTTBsTWxSVDRHT1R3UkJoVmRnT2ciLCJpc3MiOiJ6bTpjaWQ6WGVCVUVkQ0tSQjJUdVVZTUNuOG13USIsImdubyI6MCwidHlwZSI6MCwidGlkIjowLCJhdWQiOiJodHRwczovL29hdXRoLnpvb20udXMiLCJ1aWQiOiI0UHlpcXZ5dFFLeWZZcllrTUo0MFNBIiwibmJmIjoxNzM0OTM3OTYwLCJleHAiOjE3MzQ5NDE1NjAsImlhdCI6MTczNDkzNzk2MCwiYWlkIjoib0hjRnQtaXdUTTZzbXdvLTdIUEhYZyJ9.mOFMhCIxJxQIi5EAIFa47do_-R3zdm2JdDphsSzHvc8Lk2zPSnBDP-PIG4jvqiWyJH-7vkyCZqkErEksqh-eoA"

    response = requests.get(
        CHAT_MESSAGES_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    # Debugging: Print response details
    print("Chat Messages Debug:")
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve chat messages"}), response.status_code

    chat_messages = response.json().get("messages", [])
    emojis = []
    for msg in chat_messages:
        emojis.extend(extract_emojis(msg.get("message", "")))

    return jsonify({
        "chat": [msg.get("message", "") for msg in chat_messages],
        "reactions": emojis
    })

if __name__ == "__main__":
    app.run(port=5000)

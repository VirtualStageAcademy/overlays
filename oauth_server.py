import requests
from flask import Flask, redirect, request, jsonify
import re  # For extracting emojis

app = Flask(__name__)

# Replace these with your Zoom OAuth credentials
CLIENT_ID = "kPDQv5ZyQ0OQyDULYHTVmQ"
CLIENT_SECRET = "K78FIWu7Pfm9r0zzYjoCnEjlF2I9N4gg"
REDIRECT_URI = "https://obs-overlays.vercel.app/oauth/callback"

# Zoom OAuth URLs
AUTH_URL = f"https://zoom.us/oauth/authorize?response_type=code&client_id=8gZgCn_hSEmZURhhGL3PkA&redirect_uri={REDIRECT_URI}"
TOKEN_URL = "https://zoom.us/oauth/token"

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

@app.route("/")
def home():
    return f'<a href="{AUTH_URL}">Connect Your Zoom Account</a>'

@app.route("/oauth/callback")
def oauth_callback():
    auth_code = request.args.get("code")
    token_response = requests.post(
        TOKEN_URL,
        params={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    return jsonify({"access_token": access_token})

@app.route("/zoom-data/<token>")
def get_zoom_data(token):
    response = requests.get(
        "https://api.zoom.us/v2/chat/users/me/messages",
        headers={"Authorization": f"Bearer {token}"},
    )
    chat_messages = response.json().get("messages", [])
    emojis = []
    for msg in chat_messages:
        emojis.extend(extract_emojis(msg.get("message", "")))
    return jsonify({"chat": [msg["message"] for msg in chat_messages], "reactions": emojis})

if __name__ == "__main__":
    app.run(port=5000)

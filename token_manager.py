import json
import os
from base64 import b64encode
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")

TOKEN_FILE = "tokens.json"

def save_tokens(access_token, refresh_token):
    """Save tokens to a file."""
    with open(TOKEN_FILE, "w") as token_file:
        json.dump({"access_token": access_token, "refresh_token": refresh_token}, token_file)

def load_tokens():
    """Load tokens from a file."""
    try:
        with open(TOKEN_FILE, "r") as token_file:
            tokens = json.load(token_file)
        return tokens.get("access_token"), tokens.get("refresh_token")
    except FileNotFoundError:
        print("[ERROR] Token file not found.")
        return None, None

def refresh_access_token(refresh_token):
    """Refresh the OAuth access token using the refresh token."""
    token_url = "https://zoom.us/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers = {
        "Authorization": f"Basic {b64encode(f'{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}'.encode()).decode()}"
    }

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code == 200:
        tokens = response.json()
        new_access_token = tokens.get("access_token")
        new_refresh_token = tokens.get("refresh_token")
        print(f"[INFO] New access token: {new_access_token}")
        print(f"[INFO] New refresh token: {new_refresh_token}")
        return new_access_token, new_refresh_token
    else:
        print(f"[ERROR] Failed to refresh token: {response.status_code} - {response.text}")
        return None, None

